# 使用方法
## macの場合
python3 main.py \[INPUT\_FILEPATH\] \[OUTPUT\_FILEPATH\]

# 各pyファイルの機能
- \_\_init\_\_.py
モジュールの作成に必要

- check\_GSNform.py
GSN項かどうかのチェック

- debug\_info.py
デバッグ情報の定義

- GSN2json.py
ASTを出力するためのJSONファイルに変換

- main.py
各モジュールを用いて入出力を含む一連の処理を行う

- namebind.py
変数束縛に関する定義

- pgsn\_assign.py
代入処理

- pgsn\_ast.py
ASTの定義

- pgsn\_astgenerator.py
Parsingした情報からASTを作成

- pgsn\_eval.py
ASTの評価

- pgsn\_parser.py
入力した項のParsing

- PGSN2Dcom.py
出力されたPGSNのJSONファイルをD-Case Communicatorへ出力

python3 PGSN2Dcom.py \[JSON\_FILEPATH\] \[USERDATA\_FILEPATH\] \[D-Case TITLE\]

- print\_term.py
評価後の項を出力

- DCom2PGSN.py
D-Case CommunicatorのJSONファイルをPGSNのJSONファイルに変換

python3 DCom2PGSN.py \[dcaseID\] \[USERDATA\_FILEPATH\] \[OUTPUT\_FILEPATH\]

- json2GSN.py
PGSNのJSONファイルからGSN項のASTを作成

python3 json2GSN.py \[INPUT\_FILEPATH\]
