# -*- coding: utf-8 -*-

from StringIO import StringIO
from collections import namedtuple

import pytest

from parse import Book, BookManager
from parse import InvalidDocument, ElementDoesNotExist, InvalidDIVPath, NotAllowedManuscript

XML_FILE_STORAGE_PATH = "test/docs"
XML_FILE = "test/docs/test.xml"
DTD_FILE = "static/docs/grammateus.dtd"

BookManager.xml_file_storage_path = XML_FILE_STORAGE_PATH


@pytest.fixture(scope="module")
def test_book():
    return Book.open(open(XML_FILE))


def test_false_init():
    with pytest.raises(TypeError):
        Book.open(1)


def test_validation(test_book):
    # validation without success
    book = Book.open(StringIO("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <!DOCTYPE book SYSTEM "grammateus.dtd">
        <book></book>"""))
    with pytest.raises(InvalidDocument):
        book.validate(open(DTD_FILE))
    # validation with success
    assert test_book.validate(open(DTD_FILE)) is None


def test_gen_divpath_open_end():
    assert Book.gen_divpath(start_div=(1,)) == ["div[@number>=1]"]
    assert Book.gen_divpath(start_div=(1, 2)) == ["div[@number=1]/div[@number>=2]",
                                                  "div[@number>1]/div"]
    assert Book.gen_divpath(start_div=(1, 2, 3)) == ["div[@number=1]/div[@number=2]/div[@number>=3]",
                                                     "div[@number=1]/div[@number>2]/div",
                                                     "div[@number>1]/div/div"]


def test_gen_divpath_open_start():
    assert Book.gen_divpath(end_div=("7",)) == ["div[@number<=7]"]
    assert Book.gen_divpath(end_div=("7", "8")) == ["div[@number<7]/div",
                                                    "div[@number=7]/div[@number<=8]"]
    assert Book.gen_divpath(end_div=("7", "8", "9")) == ["div[@number<7]/div/div",
                                                         "div[@number=7]/div[@number<8]/div",
                                                         "div[@number=7]/div[@number=8]/div[@number<=9]"]


def test_gen_divpath_same_depth_1():
    assert Book.gen_divpath((1,), (1,)) == ["div[@number=1]"]
    assert Book.gen_divpath((1,), (2,)) == ["div[@number>=1 and @number<=2]"]
    assert Book.gen_divpath((1,), (3,)) == ["div[@number>=1 and @number<=3]"]


def test_gen_divpath_same_depth_2():
    assert Book.gen_divpath((1, 2), (1, 2)) == ["div[@number=1]/div[@number=2]"]
    assert Book.gen_divpath((1, 2), (1, 3)) == ["div[@number=1]/div[@number>=2 and @number<=3]"]
    assert Book.gen_divpath((1, 2), (1, 4)) == ["div[@number=1]/div[@number>=2 and @number<=4]"]
    # TODO: the second path is unnecessary, we should optimize it
    assert Book.gen_divpath((1, 2), (2, 4)) == ["div[@number=1]/div[@number>=2]",
                                                "div[@number>1 and @number<2]/div",
                                                "div[@number=2]/div[@number<=4]"]
    assert Book.gen_divpath((1, 2), (3, 4)) == ["div[@number=1]/div[@number>=2]",
                                                "div[@number>1 and @number<3]/div",
                                                "div[@number=3]/div[@number<=4]"]


def test_gen_divpath_same_depth_3():
    assert Book.gen_divpath((1, 2, 3), (1, 2, 3)) == ["div[@number=1]/div[@number=2]/div[@number=3]"]
    assert Book.gen_divpath((1, 2, 3), (1, 2, 4)) == ["div[@number=1]/div[@number=2]/div[@number>=3 and @number<=4]"]
    # TODO: the second path is unnecessary, we should optimize it
    assert Book.gen_divpath((1, 2, 3), (1, 3, 4)) == ["div[@number=1]/div[@number=2]/div[@number>=3]",
                                                      "div[@number=1]/div[@number>2 and @number<3]/div",
                                                      "div[@number=1]/div[@number=3]/div[@number<=4]"]
    assert Book.gen_divpath((1, 2, 3), (2, 3, 4)) == ["div[@number=1]/div[@number=2]/div[@number>=3]",
                                                      "div[@number=1]/div[@number>2]/div",
                                                      "div[@number>1 and @number<2]/div/div",
                                                      "div[@number=2]/div[@number<3]/div",
                                                      "div[@number=2]/div[@number=3]/div[@number<=4]"]


def test_gen_divpath_invalid_args():
    with pytest.raises(InvalidDIVPath):
        Book.gen_divpath((1, 2), (1,))
    with pytest.raises(InvalidDIVPath):
        Book.gen_divpath((1, 2, 3), (1, 2))
    with pytest.raises(InvalidDIVPath):
        Book.gen_divpath((2, 3), (1,))
    with pytest.raises(InvalidDIVPath):
        Book.gen_divpath((2,), (1,))
    with pytest.raises(InvalidDIVPath):
        Book.gen_divpath((2,), (1, 2))
    with pytest.raises(InvalidDIVPath):
        Book.gen_divpath((2,), (1, 2, 3))


def test_gen_divpath_diff_depth_1():
    assert Book.gen_divpath((1, 2), (3,)) == ["div[@number=1]/div[@number>=2]",
                                              "div[@number>1 and @number<=3]/div"]
    assert Book.gen_divpath((1, 2, 3), (4,)) == ["div[@number=1]/div[@number=2]/div[@number>=3]",
                                                 "div[@number=1]/div[@number>2]/div",
                                                 "div[@number>1 and @number<=4]/div/div"]
    assert Book.gen_divpath((1, 2, 3), (4, 5)) == ["div[@number=1]/div[@number=2]/div[@number>=3]",
                                                   "div[@number=1]/div[@number>2]/div",
                                                   "div[@number>1 and @number<4]/div/div",
                                                   "div[@number=4]/div[@number<=5]"]


def test_gen_divpath_diff_depth_2():
    assert Book.gen_divpath((1,), (1, 2)) == ["div[@number=1]/div[@number<=2]"]
    assert Book.gen_divpath((1,), (2, 3)) == ["div[@number>=1 and @number<2]",
                                              "div[@number=2]/div[@number<=3]"]
    assert Book.gen_divpath((1,), (3, 4)) == ["div[@number>=1 and @number<3]",
                                              "div[@number=3]/div[@number<=4]"]
    assert Book.gen_divpath((1,), (3, 4, 5)) == ["div[@number>=1 and @number<3]",
                                                 "div[@number=3]/div[@number<4]/div",
                                                 "div[@number=3]/div[@number=4]/div[@number<=5]"]
    assert Book.gen_divpath((1, 2), (3, 4, 5)) == ["div[@number=1]/div[@number>=2]",
                                                   "div[@number>1 and @number<3]/div",
                                                   "div[@number=3]/div[@number<4]/div",
                                                   "div[@number=3]/div[@number=4]/div[@number<=5]"]


def test_book_get_text(test_book):
    Text = namedtuple("Text", "unit_id, language, readings_in_unit, text")
    assert list(test_book.get_text("Greek", "TestOne", (1,))) == [Text("812", "Greek", 3, u""),
                                                                  Text("815", "Greek", 3, u"ἐλέγξαι"),
                                                                  Text("816", "Greek", 1, u"πάντας τοὺς ἀσεβεῖς,")]


def test_book_get_not_allowed_text(test_book):
    with pytest.raises(NotAllowedManuscript):
        list(test_book.get_text("Greek", "TestTwo", (1,)))


def test_book_get_text_w_wrong_args(test_book):
    # Invalid version
    with pytest.raises(ElementDoesNotExist):
        list(test_book.get_text("XGreek", "TestOne", (1,)))

    # Invalid text type
    with pytest.raises(ElementDoesNotExist):
        list(test_book.get_text("Greek", "XTestOne", (1,)))

    # Invalid start and end div points
    with pytest.raises(InvalidDIVPath):
        list(test_book.get_text("Greek", "TestOne", (2, ), (1, )))

    # Not existing start div depth
    assert list(test_book.get_text("Greek", "TestOne", (1, 2, 3, 4, 5))) == []


def test_book_get_readings(test_book):
    Reading = namedtuple("Reading", "mss, text")
    assert list(test_book.get_readings(812)) == [Reading("Gizeh", u"ὅτι ἔρχεται"),
                                                 Reading("Jude", u"ἰδοὺ ἦλθεν κύριος"),
                                                 Reading("TestOne", u"")]


def test_book_get_readings_w_wrong_args(test_book):
    assert list(test_book.get_readings(2000)) == []


## BookManager tests


def test_bookman_get_text():
    Text = namedtuple("Text", "unit_id, language, readings_in_unit, text")
    result = BookManager.get_text([{"book": "Test", "version": "Greek", "text_type": "TestOne", "start": (1,)},
                                   {"book": "Test", "version": "Greek", "text_type": "TestOne", "start": (1,)}],
                                  as_gluon=False)
    assert result == {"result": [Text("812", "Greek", 3, u""),
                                 Text("815", "Greek", 3, u"ἐλέγξαι"),
                                 Text("816", "Greek", 1, u"πάντας τοὺς ἀσεβεῖς,"),
                                 Text("812", "Greek", 3, u""),
                                 Text("815", "Greek", 3, u"ἐλέγξαι"),
                                 Text("816", "Greek", 1, u"πάντας τοὺς ἀσεβεῖς,")],
                      "error": [None, None]}


def test_bookman_get_text_w_wrong_args():
    Text = namedtuple("Text", "unit_id, language, readings_in_unit, text")

    # Invalid book name
    result = BookManager.get_text([{"book": "XTest", "version": "Greek", "text_type": "TestOne", "start": (1,)}],
                                  as_gluon=False)
    assert result == {"result": [],
                      "error": ["[Errno 2] No such file or directory: 'test/docs/XTest.xml'"]}

    # Invalid version name
    result = BookManager.get_text([{"book": "Test", "version": "XGreek", "text_type": "TestOne", "start": (1,)}],
                                  as_gluon=False)
    assert result == {"result": [],
                      "error": ["<version> element with title='XGreek' does not exist"]}

    # Invalid and valid request together
    results = BookManager.get_text([{"book": "Test", "version": "Greek", "text_type": "TestOne", "start": (1,)},
                                    {"book": "XTest", "version": "Greek", "text_type": "TestOne", "start": (1,)},
                                    {"book": "Test", "version": "Greek", "text_type": "TestOne", "start": (1,)},
                                    {"book": "Test", "version": "XGreek", "text_type": "TestOne", "start": (1,)}],
                                   as_gluon=False)
    assert results == {"result": [Text("812", "Greek", 3, u""),
                                  Text("815", "Greek", 3, u"ἐλέγξαι"),
                                  Text("816", "Greek", 1, u"πάντας τοὺς ἀσεβεῖς,"),
                                  Text("812", "Greek", 3, u""),
                                  Text("815", "Greek", 3, u"ἐλέγξαι"),
                                  Text("816", "Greek", 1, u"πάντας τοὺς ἀσεβεῖς,")],
                       "error": [None,
                                 "[Errno 2] No such file or directory: 'test/docs/XTest.xml'",
                                 None,
                                 "<version> element with title='XGreek' does not exist"]}


def test_bookman_get_text_as_gluon():
    result = BookManager.get_text([{"book": "Test", "version": "Greek", "text_type": "TestOne", "start": (1,)},
                                   {"book": "Test", "version": "Greek", "text_type": "TestOne", "start": (1,)}],
                                  as_gluon=True)
    html = '<div>' \
           '<span class="Greek 3" id="812"><a href="3">*</a></span>' \
           '<span class="Greek 3" id="815"><a href="3">{}</a></span>' \
           '<span class="Greek 1" id="816">{}</span>' \
           '</div>'.format(u"ἐλέγξαι".encode("utf-8"), u"πάντας τοὺς ἀσεβεῖς,".encode("utf-8"))
    assert str(result["result"][0]) == html
    assert str(result["result"][1]) == html
    assert len(result["result"]) == 2
    assert result["error"] == [None, None]


def test_bookman_get_readings():
    Reading = namedtuple("Reading", "mss, text")
    result = BookManager.get_readings([{"book": "Test", "unit_id": 812},
                                       {"book": "Test", "unit_id": 812}],
                                      as_gluon=False)
    assert result["result"] == [Reading("Gizeh", u"ὅτι ἔρχεται"),
                                Reading("Jude", u"ἰδοὺ ἦλθεν κύριος"),
                                Reading("TestOne", u""),
                                Reading("Gizeh", u"ὅτι ἔρχεται"),
                                Reading("Jude", u"ἰδοὺ ἦλθεν κύριος"),
                                Reading("TestOne", u"")]
    assert result["error"] == [None, None]


def test_bookman_get_readings_as_gluon():
    result = BookManager.get_readings([{"book": "Test", "unit_id": 812},
                                       {"book": "Test", "unit_id": 812}],
                                      as_gluon=True)
    html = '<dl>' \
           '<dt>Gizeh</dt><dd>{}</dd>' \
           '<dt>Jude</dt><dd>{}</dd>' \
           '<dt>TestOne</dt><dd>*</dd>' \
           '</dl>'.format(u"ὅτι ἔρχεται".encode("utf-8"), u"ἰδοὺ ἦλθεν κύριος".encode("utf-8"))
    assert str(result["result"][0]) == html
    assert str(result["result"][1]) == html
    assert len(result["result"]) == 2
    assert result["error"] == [None, None]
