from lxml import etree
from models import Rubric, RubricItem
import logging
from itertools import chain

log=logging.getLogger(__name__)

RUBRIC_VERSION=1

sample_rubric="""
<rubric>
    <category>
        <description>Grammar and Spelling</description>
        <option>Many grammatical and spelling errors</option>
        <option>This is also a text option</option>
    </category>
    <category>
        <description>Another topic to grade on</description>
        <option points="0">This is an option</option>
        <option points="1">This is another option</option>
    </category>
</rubric>
"""

def parse_task(k, xml_object):
    """Assumes that xml_object has child k"""
    return [xml_object.xpath(k)[i] for i in xrange(0,len(xml_object.xpath(k)))]

def parse(k, xml_object):
    """Assumes that xml_object has child k"""
    return xml_object.xpath(k)[0]

def stringify_children(node):
    '''
    Return all contents of an xml tree, without the outside tags.
    e.g. if node is parse of
        "<html a="b" foo="bar">Hi <div>there <span>Bruce</span><b>!</b></div><html>"
    should return
        "Hi <div>there <span>Bruce</span><b>!</b></div>"

    fixed from
    http://stackoverflow.com/questions/4624062/get-all-text-inside-a-tag-in-lxml
    '''
    # Useful things to know:

    # node.tostring() -- generates xml for the node, including start
    #                 and end tags.  We'll use this for the children.
    # node.text -- the text after the end of a start tag to the start
    #                 of the first child
    # node.tail -- the text after the end this tag to the start of the
    #                 next element.
    parts = [node.text]
    for c in node.getchildren():
        parts.append(etree.tostring(c, with_tail=True, encoding='unicode'))

    # filter removes possible Nones in texts and tails
    return u''.join(filter(None, parts))


def parse_rubric_object(rubric_xml):
    parsed_rubric=None
    try:
        parsed_rubric=etree.fromstring(rubric_xml)
    except:
        log.exception("Could not parse rubric properly.")
        return False, parsed_rubric
    try:
        parsed_category=parse_task('category', parsed_rubric)
    except:
        error_message="Cannot properly parse the category from rubric {0}".format(parsed_rubric)
        log.exception(error_message)
        parsed_category=""

    return parsed_category

def parse_rubric_item(rubric_item):
    description=""
    options=[""]
    try:
        description=stringify_children(parse('description', rubric_item))
        options=stringify_children(parse_task('option', rubric_item))
    except:
        error_message="Cannot find the proper tags in rubric item {0}".format(rubric_item)
        log.exception(error_message)

    return {'description' : description, 'options' : options}

def parse_rubric(rubric_xml):
    parsed_categories=parse_rubric_object(rubric_xml)
    parsed_rubric_items=[parse_rubric_item(pc) for pc in parsed_categories]

    return parsed_rubric_items


def generate_rubric_object(rubric_xml):
    try:
        rubric_items=parse_rubric(rubric_xml)

        for i in xrange(0,len(rubric_items)):
            rubric_row=[c.text for c in rubric_items[i]]
            text=rubric_row[0]
            score=rubric_row[1]
            max_score=rubric_row[2]
            rubric_item=RubricItem(
                rubric=rubric,
                text=text,
                score=score,
                item_number=i,
                max_score=max_score,
                finished_scoring=False,
            )
            rubric_item.save()
    except:
        log.exception("Could not save and/or parse rubric properly")
        return False, rubric

def generate_rubric_object(submission):
    rubric=Rubric(
        submission= submission,
        rubric_version=RUBRIC_VERSION,
    )


    return True, rubric





