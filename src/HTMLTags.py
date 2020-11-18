import string


class StartTag:
    """A HTML 5 start tag token."""

    def __init__(self):
        self.start = None
        self.end = None
        self.name = None
        self.self_closing = False
        self.attributes = []  # a list of [name, value] lists

    def finalize(self):
        """Convert attribute names and values to strings and then remove duplicates."""
        for attribute in self.attributes:
            attribute[0] = ''.join(attribute[0])
            attribute[1] = ''.join(attribute[1])
        self.dedup_attributes()

    def dedup_attributes(self):
        """Remove duplicate attributes. Only the first encountered attribute is retained."""
        attributes = []
        seen = set()
        for attribute in self.attributes:
            # each attribute is a list [name, value]
            if attribute[0] not in seen:
                attributes.append(attribute)
                seen.add(attribute[0])
        self.attributes = attributes

    def __str__(self):
        return "HTML 5 Start Tag\nname = %r\nself_closing = %s\nattributes = %s" % \
               (self.name, self.self_closing, self.attributes)


class HTMLStartTagParser:
    """Return a list of HTML 5 start tags in the specified string.

    Parsing follows the parsing algorithm in the HTML5 standard itself.
    The parsed tags are NOT VALIDATED in accordance with the HTML syntax.
    """

    def __init__(self, text):
        self.whitespace = '\u0009\u000A\u000C\u0020'
        self.index = 0
        self.start_tags = []
        self.current_tag = None
        self.text = text
        self.state = "DATA"
        self.parse()
        for tag in self.start_tags:
            tag.finalize()

    def get_tags(self):
        return self.start_tags

    def get_tag_strings(self):
        return [self.text[tag.start: tag.end + 1] for tag in self.start_tags]

    def parse(self):
        while self.index < len(self.text):
            if self.state == "DATA":
                self.parse_data()
            if self.state == "TAG_OPEN":
                self.parse_tag_open()
            if self.state == "TAG_NAME":
                self.parse_tag_name()
            if self.state == "BEFORE_ATTRIBUTE_NAME":
                self.parse_before_attribute_name()
            if self.state == "SELF_CLOSING_START_TAG":
                self.parse_self_closing_start_tag()
            if self.state == "ATTRIBUTE_NAME":
                self.parse_attribute_name()
            if self.state == "AFTER_ATTRIBUTE_NAME":
                self.parse_after_attribute_name()
            if self.state == "BEFORE_ATTRIBUTE_VALUE":
                self.parse_before_attribute_value()
            if self.state == "ATTRIBUTE_VALUE_DOUBLE_QUOTED":
                self.parse_attribute_value_double_quoted()
            if self.state == "ATTRIBUTE_VALUE_SINGLE_QUOTED":
                self.parse_attribute_value_single_quoted()
            if self.state == "ATTRIBUTE_VALUE_UNQUOTED":
                self.parse_attribute_value_unquoted()
            if self.state == "AFTER_ATTRIBUTE_VALUE_QUOTED":
                self.parse_after_attribute_value_quoted()

    def parse_data(self):
        # scan for less-than '<'
        if self.text[self.index] == '\u003C':
            self.current_tag = StartTag()
            self.current_tag.start = self.index
            self.index += 1
            self.state = "TAG_OPEN"
        else:
            self.index += 1
        return

    def parse_tag_open(self):
        # to be a valid HTML 5 start tag, the first character after '<' needs to be an ASCII alpha
        if self.text[self.index] in string.ascii_letters:
            self.current_tag.name = ""
            self.state = "TAG_NAME"
        else:
            self.current_tag = None
            self.state = "DATA"
        return

    def parse_tag_name(self):
        # whitespace as defined in HTML 5 standard; switch to "BEFORE_ATTRIBUTE_NAME" state
        if self.text[self.index] in self.whitespace:
            self.index += 1
            self.state = "BEFORE_ATTRIBUTE_NAME"
            return
        # solidus '/', switch to "SELF_CLOSING_START_TAG" state
        if self.text[self.index] == '\u002F':
            self.index += 1
            self.state = "SELF_CLOSING_START_TAG"
            return
        # greater-than '>'; a valid start tag has been found
        if self.text[self.index] == '\u003E':
            self.current_tag.end = self.index
            self.start_tags.append(self.current_tag)
            self.current_tag = None
            self.index += 1
            self.state = "DATA"
            return
        # ASCII upper alpha; covert to lowercase and append to tag's name
        if self.text[self.index] in string.ascii_uppercase:
            self.current_tag.name += self.text[self.index].lower()
            self.index += 1
            return
        # null character; replace with \uFFFD and append to tag's name
        if self.text[self.index] == '\u0000':
            self.current_tag.name += '\uFFFD'
            self.index += 1
            return
        # anything else; append character to tag's name
        self.current_tag.name += self.text[self.index]
        self.index += 1
        return

    def parse_self_closing_start_tag(self):
        # greater-than '>'; a valid start tag has been found
        if self.text[self.index] == '\u003E':
            self.current_tag.end = self.index
            self.current_tag.self_closing = True
            self.start_tags.append(self.current_tag)
            self.current_tag = None
            self.index += 1
            self.state = "DATA"
            return
        # anything else; reconsume in "BEFORE_ATTRIBUTE_NAME" state
        self.state = "BEFORE_ATTRIBUTE_NAME"
        return

    def parse_before_attribute_name(self):
        # whitespace; ignore
        if self.text[self.index] in self.whitespace:
            self.index += 1
            return
        # solidus '/' or greater-than '>'; reconsume in the "AFTER_ATTRIBUTE_NAME" state
        if self.text[self.index] == '\u002F' or self.text[self.index] == '\u003E':
            self.state = "AFTER_ATTRIBUTE_NAME"
            return
        # equals '='; start new attribute, set it's name to '=', and its value to the empty string,
        # switch to the "ATTRIBUTE_NAME" state
        if self.text[self.index] == '\u003D':
            self.current_tag.attributes.append([['\u003D'], [""]])
            self.state = "ATTRIBUTE_NAME"
            self.index += 1
            return
        # anything else; start new attribute, set it's name and value to the empty string and
        # reconsume in the "ATTRIBUTE_NAME" state
        self.current_tag.attributes.append([[""], [""]])
        self.state = "ATTRIBUTE_NAME"

    def parse_attribute_name(self):
        # whitespace, solidus '/' or greater-than '>'; reconsume in the "AFTER_ATTRIBUTE_NAME" state
        if self.text[self.index] in self.whitespace or \
                self.text[self.index] == '\u002F' or self.text[self.index] == '\u003E':
            self.state = "AFTER_ATTRIBUTE_NAME"
            return
        # equals '='; switch to "BEFORE_ATTRIBUTE_VALUE" state
        if self.text[self.index] == '\u003D':
            self.state = "BEFORE_ATTRIBUTE_VALUE"
            self.index += 1
            return
        # ASCII upper alpha; covert to lowercase and append to attribute's name
        if self.text[self.index] in string.ascii_uppercase:
            attribute = self.current_tag.attributes[-1]
            attribute[0].append(self.text[self.index].lower())
            self.index += 1
            return
        # null character; replace with \uFFFD and append to attribute's name
        if self.text[self.index] == '\u0000':
            attribute = self.current_tag.attributes[-1]
            attribute[0].append('\uFFFD')
            self.index += 1
            return
        # anything else; append to attribute's name
        attribute = self.current_tag.attributes[-1]
        attribute[0].append(self.text[self.index])
        self.index += 1
        return

    def parse_after_attribute_name(self):
        # whitespace; ignore
        if self.text[self.index] in self.whitespace:
            self.index += 1
            return
        # solidus '/', switch to "SELF_CLOSING_START_TAG" state
        if self.text[self.index] == '\u002F':
            self.index += 1
            self.state = "SELF_CLOSING_START_TAG"
            return
        # equals '='; switch to "BEFORE_ATTRIBUTE_VALUE" state
        if self.text[self.index] == '\u003D':
            self.state = "BEFORE_ATTRIBUTE_VALUE"
            self.index += 1
            return
        # greater-than '>'; a valid start tag has been found
        if self.text[self.index] == '\u003E':
            self.current_tag.end = self.index
            self.start_tags.append(self.current_tag)
            self.current_tag = None
            self.index += 1
            self.state = "DATA"
            return
        # anything else; start new attribute, set it's name and value to the empty string and
        # reconsume in the "ATTRIBUTE_NAME" state
        self.current_tag.attributes.append([[""], [""]])
        self.state = "ATTRIBUTE_NAME"

    def parse_before_attribute_value(self):
        # whitespace; ignore
        if self.text[self.index] in self.whitespace:
            self.index += 1
            return
        # quotation mark '"'; switch to the "ATTRIBUTE_VALUE_DOUBLE_QUOTED" state
        if self.text[self.index] == '\u0022':
            self.state = "ATTRIBUTE_VALUE_DOUBLE_QUOTED"
            self.index += 1
            return
        # apostrophe "'"; switch to the "ATTRIBUTE_VALUE_SINGLE_QUOTED" state
        if self.text[self.index] == '\u0027':
            self.state = "ATTRIBUTE_VALUE_SINGLE_QUOTED"
            self.index += 1
            return
        # greater-than '>'; missing value, add the current tag to the list and switch to "DATA" state
        if self.text[self.index] == '\u003E':
            self.current_tag.end = self.index
            self.start_tags.append(self.current_tag)
            self.current_tag = None
            self.index += 1
            self.state = "DATA"
            return
        # anything else; reconsume in the "ATTRIBUTE_VALUE_UNQUOTED" state
        self.state = "ATTRIBUTE_VALUE_UNQUOTED"
        return

    def parse_attribute_value_double_quoted(self):
        # quotation mark '"'; switch to the "AFTER_ATTRIBUTE_VALUE_QUOTED" state
        if self.text[self.index] == '\u0022':
            self.state = "AFTER_ATTRIBUTE_VALUE_QUOTED"
            self.index += 1
            return
        # anything else, including ampersand '&'; append to current attribute's value
        attribute = self.current_tag.attributes[-1]
        attribute[1].append(self.text[self.index])
        self.index += 1
        return

    def parse_attribute_value_single_quoted(self):
        # apostrophe "'"; switch to the "AFTER_ATTRIBUTE_VALUE_QUOTED" state
        if self.text[self.index] == '\u0027':
            self.state = "AFTER_ATTRIBUTE_VALUE_QUOTED"
            self.index += 1
            return
        # anything else, including ampersand '&'; append to current attribute's value
        attribute = self.current_tag.attributes[-1]
        attribute[1].append(self.text[self.index])
        self.index += 1
        return

    def parse_attribute_value_unquoted(self):
        # whitespace; switch to "BEFORE_ATTRIBUTE_NAME" state
        if self.text[self.index] in self.whitespace:
            self.state = "BEFORE_ATTRIBUTE_NAME"
            self.index += 1
            return
        # greater-than '>'; add the current tag to the list and switch to "DATA" state
        if self.text[self.index] == '\u003E':
            self.current_tag.end = self.index
            self.start_tags.append(self.current_tag)
            self.current_tag = None
            self.index += 1
            self.state = "DATA"
            return
        # null character; replace with \uFFFD and append to attribute's value
        if self.text[self.index] == '\u0000':
            attribute = self.current_tag.attributes[-1]
            attribute[1].append('\uFFFD')
            self.index += 1
            return
        # anything else, including ampersand '&'; append to current attribute's value
        attribute = self.current_tag.attributes[-1]
        attribute[1].append(self.text[self.index])
        self.index += 1
        return

    def parse_after_attribute_value_quoted(self):
        # whitespace; switch to "BEFORE_ATTRIBUTE_NAME" state
        if self.text[self.index] in self.whitespace:
            self.state = "BEFORE_ATTRIBUTE_NAME"
            self.index += 1
            return
        # solidus '/', switch to "SELF_CLOSING_START_TAG" state
        if self.text[self.index] == '\u002F':
            self.index += 1
            self.state = "SELF_CLOSING_START_TAG"
            return
        # greater-than '>'; add the current tag to the list and switch to "DATA" state
        if self.text[self.index] == '\u003E':
            self.current_tag.end = self.index
            self.start_tags.append(self.current_tag)
            self.current_tag = None
            self.index += 1
            self.state = "DATA"
            return
        # anything else; missing whitespace between tags, reconsume in the "BEFORE_ATTRIBUTE_NAME" state
        self.state = "BEFORE_ATTRIBUTE_NAME"
        return


def findtags(text):
    """Return a list of all the html start tags in the specified string."""
    parser = HTMLStartTagParser(text)
    return parser.get_tags()


def test():
    with open(r'd:\Design of Computer Programs\data\explained-ai.txt') as f:
        text = ''.join(f.readlines())
    parser = HTMLStartTagParser(text)
    for tag in parser.get_tag_strings():
        print(tag)
    print("-------------------------------------------------------------------")
    for tag in parser.get_tags():
        print(tag, '\n')


test()
