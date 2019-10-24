import re, const
from jinja2 import Template
from db_utils import db

systems = ['BITBUCKET', 'JENKINS', 'СЕРВЕРА', 'INFO']

tpl_s = "{% for s in cred %}{% if s['system'] == 'СЕРВЕРА' %}" \
        "Сервер алиас: {{ s['alias'] }}  ip: {{ s['ip'] }}  логин: {{ s['login'] }}\n" \
        "{% endif %}{% endfor %}"
tpl_b = "{% for s in cred %}{% if s['system'] == 'BITBUCKET' %}" \
        "BitBucket логин: {{ s['login'] }}\n " \
        "{% endif %}{% endfor %}"
tpl_j = "{% for s in cred %}{% if s['system'] == 'JENKINS' %}" \
        "Jenkins логин: {{ s['login'] }}\n" \
        "{% endif %}{% endfor %}"


def process_cred(statement):
    uid = statement.get_tags()[0]
    vals = re.sub(' +', ' ', str(statement)).strip().split()

    if len(vals) < 2:
        return const.wrong_command
    if vals[1].upper() == 'INFO':
        d = db.get_all_cred(uid)
        res = ''
        for tpl in [tpl_j, tpl_b, tpl_s]:
            res += Template(tpl).render(d)
        return res

    if len(vals) < 4:
        return const.wrong_command
    if vals[1].upper() not in systems:
        return "Я не заню как работать с этой системой"

    if vals[1].upper() == 'СЕРВЕРА':
        if len(vals) < 6:
            return const.wrong_command
        res = db.upsert_cred(user_id=uid, system=vals[1].upper(), login=vals[4], passwd=vals[5], alias=vals[2],
                             ip=vals[3])
    else:
        res = db.upsert_cred(user_id=uid, system=vals[1].upper(), login=vals[2], passwd=vals[3])

    return "Информация обновлена" if res else "Информация сохранена"
