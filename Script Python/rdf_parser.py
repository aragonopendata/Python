#!/usr/bin/python
# coding=utf-8
import glob
import xml.etree.ElementTree as ET
import re
import ckanclient
import sys
import config

def clean_tag(tag):
    res = tag.encode('utf-8')
    res = re.sub("[^-\\\.\wñáéíóù]", "_", res)
    return res

def clean_url(url):
    res = url.encode('utf-8').lower()
    res = re.sub("á", "a", res)
    res = re.sub("é", "e", res)
    res = re.sub("í", "i", res)
    res = re.sub("ó", "o", res)
    res = re.sub("ú", "u", res)
    res = re.sub("[^-\\\.\/:\w]", "_", res)
    return res

def upload_dataset(dataset):
    ckan = ckanclient.CkanClient(base_location=config.BASE_LOCATION, api_key=config.API_KEY)
    try:
        ckan.package_entity_put(dataset)
        print ("Dataset {} updated".format(dataset['name']))
    except ckanclient.CkanApiNotFoundError:
        try:
            ckan.package_register_post(dataset)
            print ("Dataset {} created".format(dataset['name']))
        except Exception as e:
            print ("Error while creating {}:".format(dataset['name']))
            print e
    except Exception as e:
        print ("Error while creating {}:".format(dataset['name']))
        print e

def upload_group(group):
    ckan = ckanclient.CkanClient(base_location=config.BASE_LOCATION, api_key=config.API_KEY)
    try: 
        ckan.group_register_post(group)
    except ckanclient.CkanApiConflictError:
        print ("Group {} already created, skipping".format(group['name']))
    except Exception as e:
        print ("Error while uploading group {}:".format(group['name']))
        print e
    

def dcat_tag(tag):
    return str(ET.QName(config.DCAT_NAMESPACE, tag))

def dct_tag(tag):
    return str(ET.QName(config.DCT_NAMESPACE, tag))

def rdfs_tag(tag):
    return str(ET.QName(config.RDFS_NAMESPACE, tag))

def foaf_tag(tag):
    return str(ET.QName(config.FOAF_NAMESPACE, tag))

def rdf_tag(tag):
    return str(ET.QName(config.RDF_NAMESPACE, tag))

def get_tag_text(xml, tag):
    record = xml.find(tag)
    if record is not None:
        return record.text
    else:
        return ""

def create_resources(distributions_xml):
    resources = []
    for resources_xml in distributions_xml:
        for resource_xml in resources_xml:
            resource = {}
            # resource name
            resource['name'] = get_tag_text(resource_xml, rdfs_tag('label'))
            # resource description
            resource['description'] = get_tag_text(resource_xml, dct_tag('description'))
            # resource type
            type_xml = resource_xml.find(rdf_tag('type'))
            if type_xml is not None:
                resource['type'] = type_xml.get(rdf_tag('resource'))
            # resource mime type
            format_xml = resource_xml.find(dct_tag('format'))
            if format_xml is not None:
                value_tag = '{}//{}'.format(dct_tag('IMT'), rdf_tag('value'))
                resource['mimetype'] = get_tag_text(format_xml, value_tag)
                label_tag = '{}//{}'.format(dct_tag('IMT'), rdfs_tag('label'))
                resource['format'] = get_tag_text(format_xml, label_tag)
            # resource size
            size_tag = '{}//{}//{}'.format(
                    dcat_tag('size'),
                    rdf_tag('Description'),
                    dcat_tag('bytes'))
            size_xml = resource_xml.find(size_tag)
            if size_xml is not None:
                resource['size'] = int(round(float(size_xml.text.replace(',','.'))))
            # resource url
            access_url_xml = resource_xml.find(dcat_tag('accessURL'))
            resource['url'] = clean_url(access_url_xml.get(rdf_tag('resource')))
            resources.append(resource)
    return resources

def create_groups(groups_xml):
    groups = []
    for group_xml in groups_xml:
        group = {}
        description_xml = group_xml.find(rdf_tag('Description'))
        group['title'] = get_tag_text(description_xml, rdfs_tag('label'))
        group['name'] = clean_url(get_tag_text(description_xml, dct_tag('identifier')))
        group['description'] = get_tag_text(description_xml, dct_tag('description'))
        upload_group(group)
        groups.append(group['name'])
    return groups
    dataset['groups'] = groups

def create_dataset(xml):
    dataset = {}
    extras = []
    resources = []
    # name
    dataset['name'] = get_tag_text(xml, dct_tag('identifier'))
    # description
    dataset['notes'] = get_tag_text(xml, dct_tag('description'))
    # title
    dataset['title'] = get_tag_text(xml, dct_tag('title'))
    # tags
    tags = []
    for tag_xml in xml.findall(dcat_tag('keyword')):
        tags.append(clean_tag(tag_xml.text))
    dataset['tags'] = tags
    # modified
    dataset['metadata_modified'] = get_tag_text(xml, dct_tag('modified'))
    # created
    dataset['metadata_created'] = get_tag_text(xml, dct_tag('issued'))
    # frequency 
    frequency_tag = '{}//{}//{}'.format(dct_tag('accrualPeriodicity'), 
            dct_tag('Frequency'),
            rdfs_tag('label'))
    extra = ['Frequency', get_tag_text(xml, frequency_tag)]
    if (extra[1] != ""): extras.append(extra)
    # spatial
    extra = ['Spatial', get_tag_text(xml, dct_tag('spatial'))]
    if (extra[1] != ""): extras.append(extra)
    # temporal
    extra = ['Temporal', get_tag_text(xml, dct_tag('temporal'))]
    if (extra[1] != ""): extras.append(extra)
    # language
    extra = ['Language', get_tag_text(xml, dct_tag('language'))]
    if (extra[1] != ""): extras.append(extra)
    # references
    extra = ['References', get_tag_text(xml, dct_tag('references'))]
    if (extra[1] != ""): extras.append(extra)
    # granularity
    extra = ['Granularity', get_tag_text(xml, dcat_tag('granularity'))]
    if (extra[1] != ""): extras.append(extra)
    # data quality
    extra = ['Data Quality', get_tag_text(xml, dcat_tag('dataQuality'))]
    if (extra[1] != ""): extras.append(extra)
    # data dictionary
    extra = ['Data Dictionary', get_tag_text(xml, dcat_tag('dataDictionary'))]
    if (extra[1] != ""): extras.append(extra)
    # author
    author_tag = '{}//{}//{}'.format(dct_tag('publisher'), 
            foaf_tag('Organization'),
            dct_tag('title'))
    dataset['author'] = get_tag_text(xml, author_tag)
    dataset['maintainer'] = get_tag_text(xml, author_tag)
    # url
    homepage_tag = '{}//{}//{}'.format(dct_tag('publisher'), 
            foaf_tag('Organization'),
            foaf_tag('homepage'))
    homepage_xml = xml.find(homepage_tag)
    dataset['url'] = clean_url(homepage_xml.get(rdf_tag('resource')))
    # license
    license_xml = xml.find(dct_tag('license'))
    license = license_xml.get(rdf_tag('resource'))
    if re.match(".*[Cc][Cc]-[Bb][Yy]", license):
        dataset['license_id'] = "cc-by"

    # resources
    distributions_xml = xml.findall(dcat_tag('distribution')) 
    resources = create_resources(distributions_xml)
    # groups / themes
    groups_xml = xml.findall(dcat_tag('theme'))
    groups = create_groups(groups_xml)

    dataset['resources'] = resources
    dataset['extras'] = extras
    dataset['groups'] = groups
    return dataset

def get_rdfs():
    rdfs = []
    for rdf in glob.glob(config.DOWNLOAD_PATH + "/*.rdf"):
        rdfs.append(rdf)
    return rdfs

def parse_rdfs():
    rdfs = get_rdfs()
    datasets = []
    dataset_tag = str(ET.QName(config.DCAT_NAMESPACE, 'Dataset'))
    for rdf in rdfs:
        tree = ET.parse(rdf)
        for dataset in tree.findall(dataset_tag):
            datasets.append(dataset)
            ds = create_dataset(dataset)
            upload_dataset(ds)

