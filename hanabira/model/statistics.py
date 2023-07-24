# -*- coding: utf-8 -*-
"""
"""

from sqlalchemy import *
from sqlalchemy.orm import eagerload, relation
from sqlalchemy.sql import and_, or_, not_, func
from sqlalchemy.ext.declarative import synonym_for
from sqlalchemy.dialects.mysql.base import BIGINT

from hanabira.model import meta

import logging

log = logging.getLogger(__name__)

class Stats(meta.Declarative):
    __tablename__ = "statistics_day"
    statistics_id = Column(Integer, primary_key=True)
    date          = Column(DateTime, index=True)
    range         = Column(Enum('day', 'month'), index=True)
    board_id      = Column(Integer, ForeignKey('boards.board_id'),
                           index=True)
    posts_total   = Column(Integer) # Posts+DeletedPosts
    posts_visible = Column(Integer)
    posts_deleted = Column(Integer)
    posts_invisible = Column(Integer)
    threads_new   = Column(Integer)
    threads_active= Column(Integer)
    threads_deleted = Column(Integer)
    threads_invisible = Column(Integer)
    sessions_posts = Column(Integer)
    sessions_total = Column(Integer)
    ips_posts      = Column(Integer)
    ips_total      = Column(Integer) # Get from view.log
    hits           = Column(Integer) # Get from view.log

    """
    cat ~/12.12.2010 | awk "{ print \$1; }" | sort | uniq | wc -l
    
    select date(date), weekday(date),count(display_id) as total, sum(char_length(message_raw)) as total_chars, sum(char_length(message_raw))/count(display_id) as chars_per_post, count(distinct session_id) as sessions, count(distinct ip) as ips, sum(invisible) as total_invisible, count(display_id)-sum(invisible) as total_visible from posts where date > '2010-12-23 00:00:00' and date < '2010-12-24 00:00:00' and display_id is not null;
    
    select date(date), hour(date), weekday(date),count(display_id) as total, sum(char_length(message_raw)) as total_chars, sum(char_length(message_raw))/count(display_id) as chars_per_post, count(distinct session_id) as sessions, count(distinct ip) as ips, sum(invisible) as total_invisible, count(display_id)-sum(invisible) as total_visible from posts where date > '2010-12-22 00:00:00' and date < '2010-12-23 00:00:00' and display_id is not null group by hour(date);
    """
