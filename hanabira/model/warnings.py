# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

from pylons.i18n import _, ungettext, N_, set_lang
from pylons import url
from hanabira.model.gorm import *
from hanabira.lib.ips import IP
from hanabira.lib import helpers

import logging
log = logging.getLogger(__name__)

class WarningRecord(meta.Declarative):
    __tablename__ = "warnings"
    warn_id    = Column(Integer, primary_key=True)
    date       = Column(DateTime)
    session_id = Column(String(64))
    ip         = Column(BIGINT)
    subnet     = Column(BIGINT, index=True)
    post_id    = Column(Integer, nullable=True)    
    reason     = Column(UnicodeText)
    token      = Column(String(32))
    
    @synonym_for('warn_id')
    @property
    def id(self):
        return self.warn_id
    
    def __init__(self, token, session_id, ip, post_id=None, reason=None):
        self.date = datetime.datetime.now()
        self.token = token
        self.post_id = post_id
        if isinstance(reason, list):
            reason = format_reasons_short(reason)
        self.reason = reason
        self.session_id = session_id
        ip = IP(ip)
        self.ip = ip.int
        self.subnet = ip.int & 0xFFFFFF00
        
        meta.Session.add(self)
        
    @classmethod
    def get_for_session(cls, sess):
        # Get by: session_id, first_ip subnet, last_ip subnet
        sub1 = IP(sess.created_ip).int & 0xFFFFFF00
        sub2 = IP(sess.last_ip).int & 0xFFFFFF00
        q = cls.query.filter(or_(cls.session_id == sess.id, cls.subnet.in_([sub1, sub2])))
        q = q.order_by(cls.date.desc())
        return q.limit(30).all()

reasons_list = [
    # 2.2
    (20201, u'2.2 Воспрепятствование обсуждению темы: сажа/скрыл/опхуй/тредненужен',
            u'— п.2.2, в форме выражения неудовольствия тем, что ОП создал тред с интересующей его темой; <a href="/help/subject-freedom">подробнее</a>;'),
    (20202, u'2.2 Воспрепятствование обсуждению темы: хайджек',
            u'— п.2.2, воспрепятствование обсуждению заявленной в ОП-посте темы путем намеренного размещения сообщений, переводящих дискуссию на тему, никак не связанную с заявленной в ОП-посте;'),
    (20203, u'2.2 Воспрепятствование обсуждению темы: бессмысленные сообщения/вайп',
            u'— п.2.2, воспрепятствование обсуждению заявленной в ОП-посте темы путем размещения сообщений, заведомо не связанных с темой и не несущих никакой смысловой нагрузки;'),

    # 2.3
    (20301, u'2.3 Оскорбление других пользователей',
            u'— п.2.3, оскорбительные выражения в адрес других пользователей Доброчана; <a href="/help/opinions">подробнее</a>;',
            u'оскорбление'),

    (20311, u'2.3 Нарушение культурных норм: нерусский язык',
            u'— п.2.3, общение на Доброчане ведется на русском языке; <a href="/help/language">подробнее</a>;',
            u'язык'),
    (20312, u'2.3 Нарушение культурных норм: смайлики',
            u'— п.2.3, использование т.н. "смайликов" противоречит культурным нормам Доброчана;',
            u'смайлики'),

    (20321, u'2.3 Нарушение специальных правил треда',
            u'— п.2.3, нарушено одно из специальных правил данного треда; о правилах треда можно узнать в ОП-посте или у участников треда;',
            u'правила треда'),
    (20322, u'2.3 Нарушение специальных правил треда: ORMT без рилейтеда',
            u'— п.2.3, в ORMT все сообщения должны быть с изображением одного из персонажей RM;',
            u'ОРМТ'),
    (20323, u'2.3 Нарушение специальных правил треда: ненормативные выражения',
            u'— п.2.3, в данном треде запрещена ненормативная лексика;',
            u'маты'),
    
    # 2.5
    (20501, u'2.5 Неуважение анонимности других пользователей',
            u'— п.2.5, неуважение к праву на анонимность другого пользователя, в виде сообщения о нем какой-либо персонализирующей информации или требования от него такую информацию предоставить, включая фотографии;'),
    
    # 2.6
    (20601, u'2.6 Злоупотребление средствами самоидентификации',
            u'— п.2.6, злоупотребление подписями, аватарками и другими средствами самоидентификации;'),
    
    # 2.7
    (20701, u'2.7 Незаконный контент',
            u'— п.2.7, публикация контента, который запрещено публиковать в РФ или США;'),
    
    # 2.10
    (21001, u'2.10 Некорректный рейтинг цензуры',
            u'— п.2.10, отсутствие корректного рейтинга цензуры для приложенного файла; <a href="/help/censorship-ratings">подробнее</a>;'),
    
    # 2.13
    (21301, u'2.13 Обсуждение действий модерации вне дэ',
            u'— п.2.13, обсуждение действий модерации вне предусмотренного для этого раздела (/d/);'),
    
    # 2.14
    (21401, u'2.14 Повторная публикация удаленного модерацией контента',
            u'— п.2.14, повторная публикация ранее удаленного модерацией контента;'),
    
    # 2.15
    (21501, u'2.15 Сообщение рекламного/коммерческого характера',
            u'— п.2.15, сообщение рекламного или коммерческого характера;'),
    
    ]

reasons_list_short = []
for r in reasons_list:
    reasons_list_short.append((r[0], r[1]))
    
reasons_dict = {}
for r in reasons_list:
    reasons_dict[r[0]] = r
    
message_end = u"Если у вас есть возражения или вопросы относительно данного решения модератора, вы можете их высказать <a href='/d/index.xhtml'>в разделе /d/</a>."
message_start_del = u"Ваше сообщение {post} было удалено модерацией, так как оно нарушает пункт(ы) {tos_list} <a href='/help/tos'>Условий предоставления сервиса</a>, а именно:"
message_start_warn = u"Ваше сообщение {post} нарушает пункт(ы) {tos_list} <a href='/help/tos'>Условий предоставления сервиса</a>, а именно:"
message_token = u"в связи с чем вам "
message_token_dict = {
    'forbid_post': u"отключена возможность публиковать новые сообщения",
    'forbid_name': u"отключена возможность использовать поле имя",
    'forbid_name_subj': u"отключена возможность использовать поля имя и тема",
    'forbid_files': u"отключена возможность прикреплять к сообщениям файлы",
    }
def generate_post_warn_message(reasons, post, thread, board, deleted=False, token=None):
    # 3 cases: warning, deleted, banned w/out deleting
    # with one or more reasons
    msg = []
    if deleted:
        msg.append(message_start_del)
    else:
        msg.append(message_start_warn)
        
    tos_list = []
    for r_id in reasons:
        r = reasons_dict[int(r_id)]
        msg.append(r[2])
        tos_list.append(r[1].split(' ')[0])
    tos_list = ", ".join(sorted(list(set(tos_list))))
        
    if token and not token[0] in ['premod', 'bypass_premod', 'none']:
        scope = u""
        if token[1][0] == 'board':
            scope = u" в разделе <a href='/{0}/index.xhtml'>>>/{0}/</a>".format(token[1][1])
        elif token[1][0] == 'thread':
            scope = u" в треде <a href='{2}' onmouseover=\"ShowRefPost(event,'{0}', {1}, {1});\">>>/{0}/{1}</a>".format(board.board, thread.display_id, url('thread', board=board.board, thread_id=thread.display_id))
        expires = u" до решения модератора."
        if token[2] != -1:
            nt = datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(minutes=token[2])
            expires = u" до {0} ({1} минут).".format(nt, token[2])
        msg.append(message_token + message_token_dict[token[0]] + scope + expires)
    elif not deleted:
        msg.append(u"настоятельно просим в дальнейшем при написании сообщений учитывать данные замечания и не нарушать ToS.")        
    msg.append(message_end)
    msg = u"<br/>\n".join(msg)
    thread_url = url('thread', board=board.board, thread_id=thread.display_id)
    post_link = "<a href='{2}#i{1}' onmouseover=\"ShowRefPost(event,'{0}', {3}, {1});\">>>/{0}/{1}</a>".format(board.board, post.display_id, thread_url, thread.display_id)
    msg = msg.format(tos_list=tos_list, post=post_link)
    #print msg
    return msg

def format_reasons_short(reasons=None, tokens=None):
    r = []
    if reasons:
        for r_id in reasons:
            reason = reasons_dict[int(r_id)]
            p = reason[1].split(' ')[0]
            if len(reason) >= 4:
                p += " " + reason[3]
            r.append(p)
    if tokens:
        for td in tokens:
            if 'reason_text' in td[4]:
                if isinstance(td[4]['reason_text'], list):
                    td[4]['reason_text'] = u"; ".join(td[4]['reason_text'])
                r.append(td[4]['reason_text'])
    return u"; ".join(r) + u";"

def format_token_public(tokens):
    if tokens[0][0] == 'forbid_post':
        if tokens[0][2] == -1:
            dur = u"бессрочно"
        else:
            dur = u"истекает в {0}".format(tokens[0][3] + tokens[0][2])
        return u'Вам запрещено писать сообщения в данном треде, ограничение {time}.'.format(time=dur)
    else:
        raise Exception("Unknown token type")
    
helpers.format_reasons_short = format_reasons_short