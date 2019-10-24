import const
import re
import subprocess

from db_utils import db


def process_host_info(statement):
    uid = statement.get_tags()[0]
    vals = re.sub(' +', ' ', str(statement)).strip().split()
    if len(vals) < 3:
        return const.wrong_command
    cred = db.get_cred_by_alias(uid, vals[3])
    if cred:
        command = 'ansible-playbook ./ansible/host_info.yaml -e "' \
                  ' ansible_connection=ssh ' \
                  ' ansible_ssh_user=' + str(cred['login']) + \
                  ' ansible_ssh_pass=' + str(cred['passwd'].decode('ascii')) + '" ' \
                                                                               '-i ' + str(cred['ip']) + ','
        print(command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        output, _ = process.communicate()
        output = output.decode('ascii')

        if 'failed = 0' in output:
            return output
        else:
            return "Не удалось получить информацию о сервере"

    return "Сервер '" + str(vals[3]) + "' не зарегистрированн."
