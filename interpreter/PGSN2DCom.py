import sys
import json
import requests


def main():
    print('start')
    input_path = sys.argv[1]    # PGSNインタプリタが出力するJSONファイル
    userdata_path = sys.argv[2] # D－Case Communicatorのメールアドレス&パスワード（txtファイル）

    title = sys.argv[3]

    json_open = open(input_path, 'r')
    PGSN_parts = json.load(json_open)

    with open(userdata_path) as f:
        userdata = f.readlines()
        mail = userdata[0].rstrip()
        password = userdata[1].rstrip()

    DCom_parts = []

    for part in PGSN_parts:
        part['x'] = 0
        part['y'] = 0
        part['width'] = 180
        part['height'] = 120
        if part['kind'] == 'Strategy':
            part['kind'] = 'Plan'
        DCom_parts.append(part)
    # print(DCom_parts)
    partsList = json.dumps(DCom_parts, ensure_ascii=False)

    login_data = {'mail': mail, 'passwd': password}
    r_post = requests.post(
        'https://www.matsulab.org/dcase/api/login.php', data=login_data)

    if r_post.json()['result'] == 'OK':
        authID = r_post.json()['authID']
        print(authID)
        print('Login OK')
    else:
        print('Login Error')
        return

    createDCase = {'authID': authID, 'title': title}
    r_post = requests.post(
        'https://www.matsulab.org/dcase/api/createDCase.php', data=createDCase)

    if r_post.json()['result'] == 'OK':
        dcaseID = r_post.json()['dcaseID']
    else:
        print('createDCase Error')
        return

    importDCase = {'authID': authID,
                   'dcaseID': dcaseID, 'partsList': partsList, }
    r_post = requests.post(
        'https://www.matsulab.org/dcase/api/importDCase.php', data=importDCase)
    if r_post.json()['result'] == 'OK':
        print('createDCase')
        print(f'dcaseID:{dcaseID}')
        url = 'https://www.matsulab.org/dcase/editor.html?dcaseID=' + dcaseID

        return
    else:
        print('createDCase Error')
        return


if __name__ == "__main__":
    main()
