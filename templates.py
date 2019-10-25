from jinja2 import Template
from db_utils import db

tpl_server = "{% for s in cred %}{% if s['system']|upper == 'SRV' %}" \
             "Сервер: {{ s['alias'] }}  ip: {{ s['ip'] }}  логин: {{ s['login'] }}\n" \
             "{% endif %}{% endfor %}"
tpl_bitbucket = "{% for s in cred %}{% if s['system']|upper == 'BITBUCKET' %}" \
                "BitBucket логин: {{ s['login'] }}\n " \
                "{% endif %}{% endfor %}"
tpl_jenkins = "{% for s in cred %}{% if s['system']|upper == 'JENKINS' %}" \
              "Jenkins логин: {{ s['login'] }}\n" \
              "{% endif %}{% endfor %}"


def get_cred_info(uid):
    data = db.get_all_cred(uid)
    res = ''
    for tpl in [tpl_server, tpl_bitbucket, tpl_jenkins]:
        res += Template(tpl).render(data)
    return res if res else "Записи отсутствуют"
