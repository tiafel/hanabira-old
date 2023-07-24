# -*- coding: utf-8 -*-
import os
import sys
import re
from lxml import etree
from pylons import url
from hanabira.lib.sites import parse_uri
import logging
log = logging.getLogger(__name__)

class PTO(object):
    nodes = None
    rejected = None
    def __init__(self, nodes):
        # join symbols back into strings
        self.nodes = nodes
        
    def build_etree(self, wm, parent):
        for node in self.nodes:
            if isinstance(node, PTO):
                node.build_etree(wm, parent)
            else:
                self.add_text(parent, node)
                
    def add_text(self, el, text):
        if len(el):
            if not el[-1].tail:
                el[-1].tail = ''
            el[-1].tail += text
        else:
            if not el.text:
                el.text = ''
            el.text += text
            
    def add_tag(self, parent, tag_spec, text=None, tail=None):
        if isinstance(tag_spec, tuple):
            tag = tag_spec[0]
            attrs = tag_spec[1]
        else:
            tag = tag_spec
            attrs = []
        node = etree.SubElement(parent, tag)
        for name, value  in attrs:
            node.set(name, value)
        if text:
            node.text = text
        if tail:
            node.tail = tail
        return node            
    
    def __repr__(self):
        return "<{}({})>".format(self.__class__.__name__, self.nodes)

class PTORef(PTO):
    def __init__(self, matches):
        self.board = None
        if len(matches) == 2:
            # text, display_id
            self.text = matches[0]
            self.display_id = int(matches[1])
            self.board = None
        elif len(matches) == 3:
            # text, (/)board/, display_id(optional)
            self.text = matches[0]
            self.board = matches[1]
            if self.board.startswith('/'):
                self.board = self.board[1:]
            if self.board.endswith('/'):
                self.board = self.board[:-1]
            if not matches[2]:
                self.display_id = None
            else:
                self.display_id = int(matches[2])
        else:
            raise Exception("Wrong amount of matches!")
        
    def build_etree(self, wm, parent):
        if not self.display_id:
            href = url('board', board=self.board)
            a = self.add_tag(parent, ('a', [('href', href)]), text=self.text)
            return
        if self.board:
            refboard = wm.g.boards.get(self.board)
        else:
            refboard = wm.board
        if not refboard:
            self.add_text(parent, self.text)
            return
        post = wm.reflinks.get(self.text, refboard.get_post(self.display_id))
        wm.reflinks[self.text] = post
        if not post:
            self.add_text(parent, self.text)
            return            
        href = url('thread', board=refboard.board, thread_id=post.thread.display_id) + '#i' + str(post.display_id)
        reflink = ('a', [('href', href), ('onmouseover', "ShowRefPost(event,'%s', %d, %d)"%(refboard.board, post.thread.display_id, post.display_id)), ('onclick', "Highlight(event, '%d')"%post.display_id)])
        a = self.add_tag(parent, reflink, text=self.text)
        
    def __repr__(self):
        return "<Ref({})>".format(self.text)

class PTOLink(PTO):
    def __init__(self, matches):
        rejected = []
        url = list(matches[0])
        while url and url[-1] in '*_%`':
            rejected = [url.pop()] + rejected
        self.rejected = ''.join(rejected)
        self.url = ''.join(url)
    
    def build_etree(self, wm, parent):
        a = etree.SubElement(parent, "a")
        a.set('href', self.url)
        a.text = self.url
    
class PTOLine(PTO):
    def build_etree(self, wm, parent):
        PTO.build_etree(self, wm, parent)
        etree.SubElement(parent, "br")

class PTOCite(PTO):
    def __init__(self, bql, nodes):
        self.text = " ".join(bql) + " "
        #print("text=", self.text)
        self.nodes = nodes
        #print("nodes=", self.nodes)
        self.depth = len(bql)
    
    def build_etree(self, wm, parent):
        el = etree.SubElement(parent, "blockquote")
        el.set('depth', str(self.depth - 1))
        el.text = self.text
        PTO.build_etree(self, wm, el)        
    
class PTOQuote(PTO):
    pass
        
class PTOEmp(PTOQuote):
    def build_etree(self, wm, parent):
        el = etree.SubElement(parent, "em")
        PTO.build_etree(self, wm, el)

class PTOStrong(PTOQuote):
    def build_etree(self, wm, parent):
        el = etree.SubElement(parent, "strong")
        PTO.build_etree(self, wm, el)
        
class PTOSpoiler(PTOQuote):
    def build_etree(self, wm, parent):
        el = etree.SubElement(parent, "span")
        el.set('class','spoiler')
        PTO.build_etree(self, wm, el)

    

pto_dict = {'*': PTOEmp, '_': PTOEmp, 
            '**': PTOStrong, '__':PTOStrong,
            '%%': PTOSpoiler}

pt_re = re.compile(
    "(\>\>([0-9]+))"+
    "|(\>\>(/?[a-z][0-9a-z]*/)([0-9]*))"+
    "|((([a-z]+\://)|((mailto|xmpp|bitcoin|magnet|skype)\:))[^ \t\n\r]+)"
)
pt_re_groups = [(2, PTORef), (3, PTORef), (5, PTOLink)]
    
class WakabaParser(object):
    def __init__(self, g):
        self.g = g
        return

    def parse(self, post, thread, board):
        message = WakabaMessage(post, thread, board, self.g)
        message.generate_tree()
        return message

    def parse_alone(self, text):
        message = WakabaAloneText(text, self.g)
        message.generate_tree()
        return message

class WakabaMessage(object):
    def __init__(self, post, thread, board, g):
        self.post = post
        self.thread = thread
        self.board = board
        self.text = post.message_raw.strip()
        self.g = g
        self.reflinks = {}
    
    def generate_tree(self):
        self.xml = etree.Element("div")
        self.xml.set('class','message')
        self.message_short = None
        self.total_lines_len = 0
        self.total_lines_count = 0
        self.walk_blocks()
        self.message = etree.tounicode(self.xml, pretty_print=False)
        
    def get_line_blocktype(self, line):
        line = line.strip()
        if not line:
            return 'newline'
        if line.startswith('>>'):
            return 'ref'
        if line == '``':
            return 'code'
        if line == '%%':
            return 'spoiler'
        return 'text'
        
    def push_block(self):
        # Merge ref/text together as text
        if self.blocks and (
            self.current_block_type in ('ref', 'text') and
            self.blocks[-1][0] in ('ref', 'text')):
            if self.blocks[-1][0] == 'ref':
                self.blocks[-1][0] = 'text'
                if self.blocks[-1][1][-1] == '':
                    self.blocks[-1][1].pop()
            for line in self.current_block_lines:
                self.blocks[-1][1].append(line)
        else:
            self.blocks.append([self.current_block_type, self.current_block_lines])
        self.current_block_type = None
        self.current_block_lines = []
        
    def push_nl(self):
        if self.current_block_lines and self.current_block_lines[-1] != '':
            self.current_block_lines.append('')        
    
    def push_nl_prev(self):
        # Push \n to previous block, if its okay
        if not self.blocks:
            return
        if not self.blocks[-1][1]:
            return
        if not self.blocks[-1][1][-1] == '':
            self.blocks[-1][1].append('')
        
    def parse_blocks(self):
        for line in self.lines:
            line_block_type = self.get_line_blocktype(line)
            #print("line {}, type {}".format(repr(line), line_block_type))
            if self.current_block_type is None:
                if line_block_type == 'newline':
                    self.push_nl_prev()
                    continue
                self.current_block_type = line_block_type
                if line_block_type in ('ref', 'text'):
                    self.current_block_lines.append(line)
                continue
            if self.current_block_type in ('code', 'spoiler'):
                if line_block_type in ('text', 'ref'):
                    self.current_block_lines.append(line)
                elif line_block_type == 'newline':
                    if line_block_type == 'code':
                        self.current_block_lines.append('')
                    else:
                        self.push_nl()
                elif line_block_type == self.current_block_type:
                    self.push_block()
            if self.current_block_type in ('ref', 'text'):
                if line_block_type == self.current_block_type:
                    self.current_block_lines.append(line)
                elif line_block_type == 'newline':
                    self.push_nl()
                elif line_block_type in ('code', 'spoiler', 'ref', 'text'):
                    self.push_block()
                    self.current_block_type = line_block_type
                    if line_block_type in ('ref', 'text'):
                        self.current_block_lines.append(line)
                else:
                    raise Exception("Unhandled block type {}".format(line_block_type))
        if self.current_block_lines:
            if self.current_block_type in ('code', 'spoiler'):
                self.current_block_type = 'text'
            self.push_block()
        
    def walk_blocks(self):
        self.lines = self.text.replace("\r\n", "\n").split("\n")
        # Split in independent blocks
        self.blocks = []
        self.current_block_lines = []
        self.current_block_type = None
        
        self.parse_blocks()
        #print(self.blocks)
        
        for block_type, block_lines in self.blocks:
            self.current_container = self.xml
            if block_type == 'code':
                self.current_container = etree.SubElement(self.current_container, "code")
            elif block_type == 'spoiler':
                self.current_container = etree.SubElement(self.current_container, "div")
                self.current_container.set('class','spoiler')
            for line in block_lines:
                self.walk_line(line)
    
    def walk_line(self, line):
        # cut off message_short here if it exceeds max limit
        lines_limit = int(str(self.g.settings.post.lines_limit))
        chars_limit = int(str(self.g.settings.post.chars_limit))
        if self.total_lines_count and self.message_short is None:
            if self.total_lines_count + 1 > lines_limit or \
               self.total_lines_len + len(line) > chars_limit:
                self.message_short = etree.tounicode(self.xml, pretty_print=False)
                
        # keep total amount of lines added and total length
        self.total_lines_count += 1
        self.total_lines_len   += len(line)
        
        ptl = self.tokenize_line(line)
        ptl.build_etree(self, self.current_container)        
    
    def tokenize_line_atomic(self, line):
        matches = pt_re.split(line)
        tokens = []
        tokens.append(matches.pop(0))
        while matches:            
            matched_token = None
            for tl, tc in pt_re_groups:
                token_args = []
                matched = False
                for i in range(tl):
                    ts = matches.pop(0)
                    token_args.append(ts)
                    matched = matched or (ts is not None)
                if matched:
                    matched_token = (tl, tc, token_args)
            if not matched_token:
                raise Exception("No token matched, impossible.")
            tobj = matched_token[1](matched_token[2])
            tokens.append(tobj)
            if tobj.rejected:
                tokens.append(tobj.rejected)
            tokens.append(matches.pop(0))
        return tokens
    
    def tokenize_line(self, line):
        # get atomic tokens
        tokens = self.tokenize_line_atomic(line)
        #print(tokens)
        # further tokenize strings
        bq = []
        if tokens[0].lstrip().startswith('>'):
            token0 = list(tokens[0].lstrip())
            while token0 and token0[0] in ('>', ' '):
                bqc = token0.pop(0)
                if bqc == '>':
                    bq.append(bqc)
            #print("tokens before=", tokens)
            #print("token0=", token0)
            tokens[0] = "".join(token0)
            #print("tokens after=", tokens)
        
        tokens2 = []
        for t in tokens:
            if isinstance(t, PTO):
                tokens2.append(t)
            else:
                for c in list(t):
                    tokens2.append(c)
        #print(tokens2)
        tokens = tokens2
        # re-parse remaining tokens via stack machine
        stack = []
        tokens_len = len(tokens)
        i = -1
        while i < tokens_len - 1:
            i += 1
            #print("l245 i=",i)
            #print(stack)
            t1 = tokens[i]
            if i + 1 < tokens_len:
                t2 = tokens[i+1]
            else:
                t2 = None
            if isinstance(t1, PTO):
                stack.append(t1)
                continue
            if not t1 in '*_%':
                stack.append(t1)
                continue
            
            t3 = None
            if t1 == t2 and t1 in '*_%':
                t3 = t1+t2
            elif t1 in '*_%':
                t3 = t1
                
            #print('t3=', t3)
            # if previous stack entry is of same type, append to it instead
            if stack and isinstance(stack[-1], str) and stack[-1][0] == t1:
                stack[-1] = stack[-1] + t3
                if len(t3) > 1:
                    i += 1
                continue
            
            if t3 is None:
                raise Exception("t3 is None, should not ever happen")
            if t3 == '%':
                stack.append(t3)
                continue
            
            # search stack for match, must have non-whitespace value between
            j = len(stack) - 1
            nonwhite = False
            found_start = None
            while j >= 0:
                se = stack[j]
                if isinstance(se, PTO):
                    nonwhite = True
                elif t3 in se:
                    if nonwhite:
                        found_start = j
                        break
                elif se.strip():
                    nonwhite = True
                j -= 1
            if found_start is None:
                stack.append(t3)
                if len(t3) > 1:
                    i += 1
                continue
            nodes = []
            t4 = stack.pop(found_start)
            #print('t4=', t4)
            for j in range(len(stack) - found_start):
                nodes.append(stack.pop(found_start))
            t5 = pto_dict[t3](nodes)
            if len(t3) < len(t4):
                stack.append(t1 * (len(t4) - len(t3)))
            if len(t3) > 1:
                i += 1                
            stack.append(t5)
            #print(stack)
        # finished
        if bq:
            bqobj = PTOCite(bq, stack)
            return bqobj
        return PTOLine(stack)

class WakabaAloneText(WakabaMessage):
    def __init__(self, text, g):
        self.post = None
        self.thread = None
        self.board = None
        self.text = text
        self.g = g
        self.reflinks = {}

    def cut_to_limit(self):
        return False