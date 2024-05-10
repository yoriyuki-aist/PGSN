import sys
import json
import requests


def main():
    print('start')
    dcaseID = sys.argv[1]   # PGSNに変換させたいD-CaseのdcaseID
    userdata_path = sys.argv[2]     # ユーザデータのパス+ファイル名
    output_path = sys.argv[3]    # 出力先のパス+ファイル名

    with open(userdata_path) as f:  # ユーザデータ(D-Case Communicator)の読み込み
        userdata = f.readlines()
        mail = userdata[0].rstrip() # メールアドレス
        password = userdata[1].rstrip() # パスワード

    DCom_parts = []
    PGSN_parts = []

    # ログイン処理
    login_data = {'mail': mail, 'passwd': password}
    r_post = requests.post(
        'https://www.matsulab.org/dcase/api/login.php', data=login_data)

    if r_post.json()['result'] == 'OK':
        authID = r_post.json()['authID']
        print(f'authID:{authID}')
        print('Login OK')
    else:
        print('Login Error')    # ログインエラー
        return

    # DCaseのエクスポート
    exportDCase = {'authID': authID,
                   'dcaseID': dcaseID }
    r_post = requests.post(
        'https://www.matsulab.org/dcase/api/exportDCase.php', data=exportDCase)
    if r_post.json()['result'] == 'OK':
        print('exportDCase')
        DCom_parts = r_post.json()['partsList']

    else:
        print('exportDCase Error')  # エクスポートエラー
        return
    
    # D-Case CommunicatorのデータをPGSNのJSONに変換
    for part in DCom_parts:
        # ここにHTMLのタグの除去処理を追加する
        if part['kind'] == 'Plan':  
            part['kind'] = 'Strategy'
        PGSN_parts.append({'partsID': part['partsID'], 
                           'parent': part['parent'],
                           'children': part['children'], 
                           'kind': part['kind'], 
                           'detail': part['detail']})

    with open(output_path, 'w') as f:
        json.dump(PGSN_parts, f, ensure_ascii=False)

if __name__ == "__main__":
    main()
