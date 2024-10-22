# -coding: utf-8 -
# instance_id = 'i-03df3f0f1f4644192'

#1-1. 分割ファイルの番号を入れる。220528
sep_num = '3'

## #第一ブロック 必要なモジュール類をインポート

##EC2、ローカルの切り替え。220324
media_name = 'マイナビ転職'
file_media_name = 'mynavi'


#instancd-idを自動取得するロジック。230923
import requests
import time

def get_instance_id(retries=3, delay=5):
    url = "http://169.254.169.254/latest/meta-data/instance-id"
    for i in range(retries):
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        # リトライする前に少し待機します。
        time.sleep(delay)
    return None

instance_id = get_instance_id()
if instance_id:
    print("Instance ID:", instance_id)
else:
    print("Failed to fetch instance ID after 3 retries.")
    #6-2, ec2起動開始のメール送信。211221
    # 以下にGmailの設定を書き込む★ --- (*1)
    gmail_account = "bhmarketing96010@gmail.com"
    #二段階認証に変更。211027
    gmail_password = "krsvljvzbqwaflgl"
    # メールの送信先★ --- (*2)
    mail_to = "baklis@blueheats.com"

    # メールデータ(MIME)の作成 --- (*3)
    # msj = logger.info(media_name + "の収集が完了しました。")
    # subject = msj

    #もしlogger内容でメール送信できなければ、↓に変更する。
    now = datetime.datetime.now()
    now_time = f"{now:%Y-%m-%d %H:%M:%S}"
    subject = now_time + '【' + file_media_name + '_' + str(sep_num) + "】のinstance_idが取得できませんでした。注意してください。"

    #本文はブランクでOK。211210
    body = file_media_name + '_' + str(sep_num) + " のinstance_idが取得できませんでした。注意してください。"

    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["To"] = mail_to
    msg["From"] = gmail_account

    # Gmailに接続 --- (*4)
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465,
        context=ssl.create_default_context())
    server.login(gmail_account, gmail_password)
    server.send_message(msg) # メールの送信
    # print("メール送信 complete.")
    logger.info("メール送信 complete.")


#gecko化。220714
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)

#EC2用マスター
chrome_driver_path_ec2 = '/usr/local/bin/chromedriver'
output_path_ec2 = '/home/ec2-user/' + file_media_name + '_csv_files_s/'
judge_file_path_ec2 = '/home/ec2-user/'
#ローカル用マスター
chrome_driver_path_local = '/Users/yusukekurimoto/Dropbox/210226baklis_scr_files/chromedriver98'
output_path_local = '/Users/yusukekurimoto/Dropbox/210226baklis_scr_files/201111bak_csv_files/'
judge_file_path_local = '/Users/yusukekurimoto/Dropbox/210226baklis_scr_files/'


#EC2用切り替え
chrm_path = chrome_driver_path_ec2
output_path = output_path_ec2
judge_file_path = judge_file_path_ec2

#ローカル用切り替え
# chrm_path = chrome_driver_path_local
# output_path = output_path_local
# judge_file_path = judge_file_path_local



#1. 必要なモジュールをインポート
import time
t1 = time.time()
#
import pandas as pd
from lxml import html
from selenium import webdriver
#201122 想定される例外を3つインポート
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
#210409 新規にエラーを追加
from selenium.common.exceptions import UnexpectedAlertPresentException
import re
#↓追記201202
import os
import csv
import datetime
#xlsx形式で吐き出すため追記。211210
import openpyxl
from openpyxl.styles.fonts import Font
from line_profiler import LineProfiler
import pattern_text as pt
pat = pt.get_pattern_text()
#ここでptを塗り替えてしまってる、、ゆくゆく直す
import city_pattern_text as pt
city_pat = pt.get_city_pattern_text()
#栗本自作『都道府県補完』モジュール。220324
import complement_pref as cp
#メール送信のモジュールをインポート。211024
import smtplib, ssl
from email.mime.text import MIMEText
#ファイル作成のライブラリをインポート。211208
import pathlib

#半角化のモジュール。221109
import unicodedata

from selenium.webdriver.common.by import By

#S3アップロード用のライブラリをインポート。230608
import boto3
from botocore.exceptions import ClientError
import os
import requests

#ロギングのインポート。211024
import logging
#1, ロガーの生成
logger = logging.getLogger(__name__)
#2, 出力レベルの設定
logger.setLevel(logging.INFO)

#3-1, ファイルハンドラの設定
today = datetime.datetime.today()
log_file_name = '{0:%y%m%d}'.format(today) + file_media_name + '_.log'
f_handler = logging.FileHandler(output_path + log_file_name)
logger.addHandler(f_handler)
#3-2, ストリームハンドラの設定
s_handler = logging.StreamHandler()
logger.addHandler(s_handler)
#4-1, フォーマッタの生成
fmt = logging.Formatter('%(asctime)s %(message)s _%(levelname)s')
#4-2,ハンドラにフォーマッタを登録
f_handler.setFormatter(fmt)
s_handler.setFormatter(fmt)


#Chromedriverバージョンアップ2009011730
driver = webdriver.Firefox(options=options)
driver.implicitly_wait(10)
#ページの読み込み最大待ち時間の指定する
driver.set_page_load_timeout(40)
#crash対策 201130
driver.set_window_size(500, 500)


#1-2. 空のdfを作っておく。
heading_columns = ['求人ID', '企業ID', '取得日', '媒体名', '社名', '法人名', '法人名補足', '電話番号', '電話番号ハイフンなし',
                                   '掲載期間', '掲載開始日', '情報更新日', '掲載終了日', '職種大分類', '職種中分類', '職種小分類',
                                   '掲載社名', '媒体記載職種', '事業内容', '本社住所', '業種', '従業員数', '資本金', '売上高',
                                   '設立', '勤務地', '給与', '勤務時間', '待遇・福利厚生', '休日・休暇', '仕事内容',
                                   '求めている人材', '雇用区分', 'メールアドレス',
                                   '郵便番号', 'お問合せ住所', '採用担当', '募集背景', 'お問合せ都道府県', 'お問合せ市区町村',
                                   'お問合せ町域', '広告プラン', '掲載URL', '企業HP', '従業員数レンジ', '未経験フラグ', 
                                    '転勤なしフラグ', '設立年数値', '株式公開フラグ', '資本金レンジ', '派遣会社フラグ', 
                                   '給与区分', '給与下限(万円)', '給与上限(万円)', '英語スキルフラグ', '外国籍活躍フラグ', '想定決算月', '売上高レンジ']
df_info = pd.DataFrame(columns = heading_columns)
    
#3-2. 要素有り、無し分岐の独自関数を定義
def check_exists_element(element):
    try:
        driver.find_element(By.CSS_SELECTOR,element)
        return True
    except NoSuchElementException:
        return False

###2. 【番号取得ロジック_現時点の完成形】230104   
def gen_phone_num(text_ele):
    #半角に修正してからメールアドレス取得ロジックでテスト。221109
    text_normal = unicodedata.normalize("NFKC", text_ele)
    phone_number = re.search(r'0\d{1,3}[-ｰーーーｰ‐－（()）]\d{2,4}[-ｰーーーｰ‐－（()）]\d{3,4}', text_normal)
    if not phone_number:
        phone_number = ''
        phone_number_nonehyphen = ''
    else:
        phone_number = phone_number.group()
        phone_number = re.sub(r'[-ｰーーーｰ‐－（()）]', '-', phone_number)
        phone_number_nonehyphen = re.sub(r'[-ｰーーーｰ‐－（()）]', '', phone_number)

    return (phone_number, phone_number_nonehyphen)

###3. 【メアド取得ロジック_現時点の完成形】230104
def gen_mail_ad(text_ele):
    td_text_normal = unicodedata.normalize("NFKC", text_ele)
    mail_address = re.search(r'[a-zA-Z0-9\.\-_+\']+[@＠][\w\.-]+\.[a-zA-Z]{2,}', td_text_normal)
    if not mail_address:
        mail_address = ''
    else:
        mail_address = mail_address.group()
    return mail_address

###4. 法人名抽出の独自関数を定義。230129
def gen_cor_name(company_name):

    #1-1-1.まずは、純粋な法人名を割り出す。
    #はたらいくは|(株)|（株）|(有)|を株式会社、有限会社に置き換える処理を入れる。201220
    #'㈱'を追加。230105
    company_name = company_name.replace('(株)', '株式会社').replace('（株）', '株式会社').replace('(有)', '有限会社').replace('（有）', '有限会社').replace('(医社)', '医療法人社団').replace('(医)', '医療法人').replace('(社)', '社団法人').replace('㈱', '株式会社')
    corporate_name = company_name.replace(' ', '').replace('　', '')
    legal_status_num = company_name.count('株式会社')

    legal_personality = re.search(r'^(?=.*(株式会社|有限会社|合同会社|学校法人|医療法人|社会福祉法人|事務所|独立行政法人|相互会社|生活協同組合|公益社団法人|特定非営利活動法人|企業組合|一般社団法人|社会医療法人|社会保険労務士法人|日本赤十字社|中国国際航空公司|税理士法人|NPO法人|国立大学法人|国立研究開発法人|ハイウェイ協同組合|行政書士法人|公益財団法人|一般財団法人)).*$', company_name)

    #1-1-2. パターン①『合同募集』案件時の処理。
    if '合同募集' in company_name:
        corporate_name = corporate_name.replace(' ', '').replace('　', '')
        corporate_name = corporate_name.replace('営業職', '').replace('各社', '')

        corporate_name = re.sub(r'(?<=グループ).*', '', corporate_name)
        corporate_name = re.sub(r'合同募集.*', '', corporate_name)
        corporate_name = re.sub(r'[】\(\（\(\（\（\（\）\）\）\)\）\)/／◆「」『』※＊～~<>＜＞≪≫|★◎、〈〉\[\]〔〕《》{}].*', '', corporate_name)
        #先頭にくる『【』だけ先に取る。dodaで『【ホットスタッフ広島グループ合同募集】株式会社ホットスタッフ広島、株式会社ホットスタッフ五日市』こういうケースがあるから。230115
        corporate_name = re.sub(r'^【', '', corporate_name)
        corporate_name = re.sub(r'【.*', '', corporate_name)

    #1-1-2-2. パターン①-2 エンの合同募集表記に対応。法人格が3つ以上、かつ「グループ」が含まれる場合。『ライフエージェントグループ（株式会社エールーム、株式会社アクセス、株式会社ライフアシスト）』
    elif legal_status_num >= 3 and 'グループ' in company_name:
        corporate_name = corporate_name.replace(' ', '').replace('　', '')
        corporate_name = re.sub(r'(?<=グループ).*', '', corporate_name)
        corporate_name = re.sub(r'合同募集.*', '', corporate_name)
        corporate_name = re.sub(r'[】\(\（\(\（\（\（\）\）\）\)\）\)/／◆「」『』※＊～~<>＜＞≪≫|★◎、〈〉\[\]〔〕《》{}].*', '', corporate_name)
        #先頭にくる『【』だけ先に取る。dodaで『【ホットスタッフ広島グループ合同募集】株式会社ホットスタッフ広島、株式会社ホットスタッフ五日市』こういうケースがあるから。230115
        corporate_name = re.sub(r'^【', '', corporate_name)
        corporate_name = re.sub(r'【.*', '', corporate_name)


    #1-1-3. パターン②法人格が含まれない場合は、スペースの間を削除し、記号を削除して終了。
    elif not legal_personality:
        corporate_name = re.sub(r'[\(\（\(\（\（\（【<＜≪～~〔〈\[〔《{「『].+[\）\）\）\)\）\)】>＞≫～~〕〉\]〕》}」』]', '', corporate_name)
        corporate_name = re.sub(r'[【】\(\（\(\（\（\（\）\）\）\)\）\)/／◆「」『』※＊～~<>＜＞≪≫\|★◎、〈〉\[\]〔〕《》{}]', '', corporate_name)
        corporate_sup = ''

    #1-1-4. パターン③【通常の株式会社◯◯の場合】『合同募集』が含まれず、かつcompany_nameに法人格が含まれる場合の処理。230105            
    else:

        #記号に囲まれた（or 会社名の後ろに記号＋修飾語が来ている）ケースの社名を抜き取るロジック。230116
        check_ele = re.search(r'[^(\(\（\(\（\（\（【<＜≪～~〔〈\[〔《「『{◆※＊～~\|★◎、\）\）\）\)\）\)】>＞≫～~〕〉\]〕》\/／」』})]*(株式会社|有限会社|合同会社).*?[\(\（\(\（\（\（【<＜≪～~〔〈\[〔《「『{◆※＊～~\|★◎、\）\）\）\)\）\)】>＞≫～~〕〉\]〕》\/／」』})]', corporate_name)
        if check_ele:
            corporate_name = check_ele.group()
            #余計な記号を削除する。
            corporate_name = re.sub(r'[\(\（\(\（\（\（【<＜≪～~〔〈\[〔《「『{◆※＊～~\|★◎、\）\）\）\)\）\)】>＞≫～~〕〉\]〕》\/／」』}]', '', corporate_name)

    #スペースでsplitするから、スペース削除をする前のcompany_nameを使用する。230115
    split_name_li = re.split('[ 　【】\(\（\(\（\（\（\）\）\）\)\）\)/／◆「」『』※＊～~<>＜＞≪≫\|★◎、〈〉\[\]〔〕《》{}]', company_name)
    for split_name in split_name_li:
        #法人名補足を削除するため、事業部名、店舗名などがつくワードを洗い出す。
        #前部は含まれると除かれたくない単語、後部は含まれると除く単語。どんどん追加していく。
        #つまり、法人格がつかず、『◯◯事業所』などがつくワードを炙り出している。230105

        #check_1では法人格の有無をチェック。
        corporate_check_1 = re.search(r'.*(株式会社|有限会社|合同会社|学校法人|医療法人|社会福祉法人|独立行政法人|相互会社|事務所|生活協同組合|公益社団法人|特定非営利活動法人|特定医療法人|企業組合|一般社団法人|社会医療法人|国立研究開発法人|NPO法人|会計事務所|宗教法人|行政書士法人|公益財団法人|一般財団法人).*', split_name)
        #check_2では不要な語尾の修飾語をチェック。230116
        corporate_check_2 = re.search(r'.*(佐賀製作所|キッズクリニック鷺沼|直取引|ダスキン津田|オフィス迎賓館|転職エージェント|飯田橋駅前教室|グループ傘下|東京中央美容外科|西日本ユニット|HRバリュー事業|IT派遣|関東事務所|東海ブロック|関西事務所|明聖高等学校|中野キャンパス|おおしま皮膚科|お寺でおみおくり|ジャック幼児教育研究所|曙ゴルフガーデン|スイーツ新大阪|大阪南部ブロック|第一倉庫|名古屋オフィス|東中部カンパニー|経営企画本部|ナレッジバンク|モバイルユニット|住居余暇本部|友愛記念病院|ホームブリスイン野田|きらら歯科|携われる|建物管理|横浜アクア|そよかぜ|清風霊園|開設準備室|ふれあい館|ビジネススペあいの郷|ＩＴサービス室|GS1Japan|社名変更|東急不動産|住友商事|ー東証一部上場ー|ステーション綾瀬|整備工場|ー北海道空港グループー|ズ・ジャパン|だらぼち|和食居酒屋|北関東カンパニー|遊び|学ぶ|小中部|高校部|続けています。|指導キャンパス|DEC統括|M-Shine|町CS|STLASSH|事業局|くるみの森保育園|北部ステーション|イベント事務局|播磨自動車教習所|北口教室|大宝塚ゴルフクラブ|大阪西店|土佐堀|南部ブロック|老人ホーム|東住吉|にっこり山城|名古屋商科大学|飛鳥未来高等学校|名古屋キャンパス|モバイルユニット|山内会計事務所|みなとみらい耳鼻咽喉科|観洋|出資|上場企業|グループ企業|上場|つつじ荘|のとだらぼち|生活事業|出資会社|出資企業|こうのとり|LANDooZ|個別指導キャンパス|子会社|むらた整形外科クリニック|OHARADENTALCLINIC|ハレルヤ園|地域包括ケア推進課|こども歯科|品川美容外科|通りデンタルケア|山本歯科|保谷伊藤眼科|クリニック鴨居|パートナー川口|玉成苑|野方駅内科|ウォーク尾久|田北整形外科|木場訪問看護ステーション|クリニック吉祥寺|たかの整形外科|ワダ矯正歯科|銀座･にわ歯科室|つるい整形外科|みよし歯科|銀座院|東京皮膚科･形成外科|船州会歯科診療所|宮田歯科三田診療所|瑞江整形外科|Workit!Plaza福岡|広島カンパニー|UCCグループ|CafeRestaurantBinario|アウル運輸サービス|カワイ体育教室|D-Plus|家庭教師のマナベスト|ゆかり|白鳩保育園|ダイア磯子|児童デイサービスくろーばー|CENTURY21|センチュリー21|部|課|オフィス|事業部|事業所|支社|支店|営業所|医院|クリニック|病院|本社|車庫|学院|ハブセンター|本舗|エリア|ダスキン津田|支部|幼児教室|駅前|分室|部門|サポートグループ|ブロック|藤枝校|春日井校|事務管理センター|教育グループ|外科|Group|研修センター|ミスミグループ|推進室|クラブグループ|DSグループ|みやび鯛グループ|本部|開発グループ)$', split_name)
        #split_nameに法人格が入っていなく、不要な修飾語が入っている場合。
        if not corporate_check_1 and corporate_check_2:
            corporate_check_2 = corporate_check_2.group()
            #corporate_nameから不要な修飾語（事業部、支社など）を削除していく。
            corporate_name = corporate_name.replace(corporate_check_2, '')

    # #『有限会社』 and 『店』がつく時は削除しない。（corporate_check_2から『店』を省いたのでコメアウト）230117
    # if '有限会社' in company_name and '店' in company_name:
    #     corporate_name = company_name.replace(' ', '').replace('　', '')

    #4-4-0.『法人名補足』を抽出する。
    #法人名補足を入れる箱を作る。
    corporate_sup = ''
    #4-4-1.括弧で分割し、事業部名などが含まれるものを抽出する。
    split_name_li = re.split('[【】（）()/／◆「」『』※＊～~<>＜＞≪≫|★◎、〈〉\[\]〔〕《》{}]', company_name)
    for split_name in split_name_li:
        #事業部名、店舗名などがつくワードを検索
        corporate_sup_ele_1 = re.search(r'^(?!.*株式会社|有限会社|合同会社|学校法人|医療法人|社会福祉法人|独立行政法人|相互会社|事務所|生活協同組合|公益社団法人|特定非営利活動法人|特定医療法人|企業組合|一般社団法人|社会医療法人|国立研究開発法人|NPO法人|会計事務所|三協管理センター|鍋浦のこ目立センター｜大宮商店|船橋中央自動車学校|小室商店|藤木商店|笠川工務店|伊藤工務店|広報企画センター|西商店|二村商店|サカイ引越センター|前田営工センター|岡田商店|左近商店|伊藤商店|日本衛生センター|クリエーションセンター|永岡医院|岩江クリニック|門田医院|鴨居病院|江口医院|苅安賀自動車学校|冨士喜本店|井上清助商店|ゆびすい労務センター|神田歯科医院|東京広域事務センター|大塚製薬工場|東京個別指導学院|コーディネーションセンター|キャリアデザインセンター|研究支援センター|技術研究センター|サンタックオフィス|谷田病院|JFR情報センター|木村屋|阿部長商店|がん研究センター|早田工務店|分析センター|近藤建材店|中央グループ|鈴木工務店|中央労務オフィス|臨床検査センター|法研中部|みつもりデンタル|らくだケア|サンタックス|くまの歯科|明石市立市民病院|よしだ歯科|今治繊維|九州建設|大川インテリア|丸喜工務店|太田歯科医院|かじはら歯科|五十子|神田ウィメンズ|日本建築センター|ＪＰＣＥＲＴ|椿デンタル|長澤工務店|亜細亜友の会|日本スポーツ振興|飯田商店|アエラ小児|広沢自動車学校|紛争処理|吉山塗料店|石井工務店|モリカワ会計|シルバー人材|埼玉県産業|日本会計|札幌ハート|鈴木酒造店|豊能障害|花巻病院|バウムクーヘン|広島平和|甲府昭和店|新町クリニック|欧州連合|京都ジョブパーク|新情報センター|インターオフィス|タックスオフィス|神戸海星病院|Nidec|早田工務店|熊谷環境分析センター|近藤建材店|富士学院|貝沼商店|ミニクリーン中部|法研中部|加藤工務店|明石市立市民病院|堀田工務店|今治繊維リソースセンター|九州建設マネジメントセンター|社会医療法人聖ルチア会|八幡病院|丸喜工務店|機能訓練センター|長澤工務店|亜細亜友の会外語学院|吉田クリニック|健康長寿医療センター|社会保険労務士法人|川越市シルバー|上野村きのこセンター|国民生活センター|マンション住替|儀間商店|東京紙店|木下商店|共立メンテナンスグループ|萩原商店|Ｔ.クリエーションセンター).*(佐賀製作所|キッズクリニック鷺沼|直取引|ダスキン津田|オフィス迎賓館|転職エージェント|飯田橋駅前教室|グループ傘下|東京中央美容外科|西日本ユニット|HRバリュー事業|IT派遣|関東事務所|東海ブロック|関西事務所|明聖高等学校|中野キャンパス|おおしま皮膚科|お寺でおみおくり|ジャック幼児教育研究所|曙ゴルフガーデン|スイーツ新大阪|大阪南部ブロック|第一倉庫|名古屋オフィス|東中部カンパニー|経営企画本部|ナレッジバンク|モバイルユニット|住居余暇本部|友愛記念病院|ホームブリスイン野田|きらら歯科|携われる|建物管理|横浜アクア|そよかぜ|清風霊園|開設準備室|ふれあい館|ビジネススペあいの郷|ＩＴサービス室|ほけんの窓口|GS1Japan|社名変更|東急不動産|住友商事|ー東証一部上場ー|ステーション綾瀬|整備工場|ー北海道空港グループー|ズ・ジャパン|だらぼち|和食居酒屋|北関東カンパニー|遊び|学ぶ|小中部|高校部|続けています。|指導キャンパス|DEC統括|M-Shine|町CS|STLASSH|事業局|くるみの森保育園|北部ステーション|イベント事務局|播磨自動車教習所|北口教室|大宝塚ゴルフクラブ|大阪西店|土佐堀|南部ブロック|老人ホーム|東住吉|にっこり山城|名古屋商科大学|飛鳥未来高等学校|名古屋キャンパス|モバイルユニット|山内会計事務所|みなとみらい耳鼻咽喉科|観洋|出資|上場企業|グループ企業|上場|つつじ荘|のとだらぼち|生活事業|出資会社|出資企業|こうのとり|LANDooZ|個別指導キャンパス|子会社|むらた整形外科クリニック|OHARADENTALCLINIC|ハレルヤ園|地域包括ケア推進課|こども歯科|品川美容外科|通りデンタルケア|山本歯科|保谷伊藤眼科|クリニック鴨居|パートナー川口|玉成苑|野方駅内科|ウォーク尾久|田北整形外科|木場訪問看護ステーション|クリニック吉祥寺|たかの整形外科|ワダ矯正歯科|銀座･にわ歯科室|つるい整形外科|みよし歯科|銀座院|東京皮膚科･形成外科|船州会歯科診療所|宮田歯科三田診療所|瑞江整形外科|Workit!Plaza福岡|広島カンパニー|UCCグループ|CafeRestaurantBinario|アウル運輸サービス|カワイ体育教室|D-Plus|家庭教師のマナベスト|ゆかり|白鳩保育園|ダイア磯子|児童デイサービスくろーばー|CENTURY21|センチュリー21|部|課|オフィス|事業部|事業所|支社|支店|店|営業所|工場|医院|クリニック|病院|本社|車庫|学院|ハブセンター|センター|本舗|エリア|ダスキン津田|支部|幼児教室)$', split_name)   
        if corporate_sup_ele_1:
            corporate_sup_ele_1 = corporate_sup_ele_1.group()
            corporate_sup += corporate_sup_ele_1 + ','

        #4-4-2.最後の","を削除
        corporate_sup = re.sub(r',$', '', corporate_sup)

    #『株式会社ＫＥＹＰＡＳＳ(学校法人栗原学園グループ)』のケースを回避。230119
    key_name = '株式会社'
    if not key_name in company_name:


        #『社会福祉法人』などの切り分けロジック。社会医療法人追記。210726
        corporate_name_jad = company_name
        corporate_name_jad = corporate_name_jad.replace(' ', '').replace('　', '')      
        #『社会福祉法人』などの切り分けロジック。210722
        if '社会医療法人' in corporate_name_jad:
            #'社会医療法人.+?会'←の箇所、『?』が入ると最短一致になる。230105
            corporate_name_ele = re.search(r'社会医療法人.+?会', corporate_name_jad)
            #『社会福祉法人』より後方に『会』が入っている場合の処理。
            if corporate_name_ele:
                corporate_name = corporate_name_ele.group()       
                corporate_sup = corporate_name_jad.replace(corporate_name, '')

        elif '一般社団法人' in corporate_name_jad or '医療法人' in corporate_name_jad:
            corporate_name_ele = re.search(r'.+会', corporate_name_jad)
            #『会』が入っている場合の処理。
            if corporate_name_ele:
                corporate_name = corporate_name_ele.group()
                corporate_sup = corporate_name_jad.replace(corporate_name, '')
            #company_nameに『会』が含まれない場合は、最後で記号を省く。230119
            else:
                corporate_name = corporate_name_jad

        elif '社会福祉法人' in corporate_name_jad:
            corporate_name_ele = re.search(r'社会福祉法人.+?(?<!社)会', corporate_name_jad)
            #『社会福祉法人』より後方に『会』が入っている場合の処理。
            if corporate_name_ele:
                corporate_name = corporate_name_ele.group()
                corporate_sup = corporate_name_jad.replace(corporate_name, '')
            else:
                corporate_name_ele = re.search(r'社会福祉法人.+?園', corporate_name_jad)
                if corporate_name_ele:
                    corporate_name = corporate_name_ele.group()
                    corporate_sup = corporate_name_jad.replace(corporate_name, '')

        elif '学校法人' in corporate_name_jad:
            corporate_name_ele = re.search(r'学校法人.+?園', corporate_name_jad)
            #『園』が入っている場合の処理。
            if corporate_name_ele:
                corporate_name = corporate_name_ele.group()
                corporate_sup = corporate_name_jad.replace(corporate_name, '')

        #記号に囲まれた（or 会社名の後ろに記号＋修飾語が来ている）ケースの社名を抜き取るロジック。230116
        check_ele = re.search(r'[^(\(\（\(\（\（\（【<＜≪～~〔〈\[〔《「『{◆※＊～~\|★◎、\）\）\）\)\）\)】>＞≫～~〕〉\]〕》\/／」』})]*(社会医療法人|一般社団法人|医療法人|社会福祉法人|学校法人).*?[\(\（\(\（\（\（【<＜≪～~〔〈\[〔《「『{◆※＊～~\|★◎、\）\）\）\)\）\)】>＞≫～~〕〉\]〕》\/／」』})]', corporate_name)
        if check_ele:
            corporate_name = check_ele.group()

    #『いやしのもりクリニック』みたく、corporate_nameがブランクになってしまうケースを回避。230122
    if not corporate_name:
        corporate_name = company_name.replace(' ', '').replace('　', '')
        
    #『株式会社』だけの場合を回避。230128
    check_ele = re.search(r'^(株式会社|有限会社|合同会社|社会福祉法人|社会医療法人|医療法人|医療法人社団|一般社団法人|学校法人)$', corporate_name)
    if check_ele:
        corporate_name = company_name.replace(' ', '').replace('　', '')

    #最後に余計な記号を削除する。
    corporate_name = corporate_name.replace('（仮）', '').replace('(仮)', '')
    corporate_name = re.sub(r'[\(\（\(\（\（\（【<＜≪～~〔〈\[〔《「『{◆※＊～~\|★◎、\）\）\）\)\）\)】>＞≫～~〕〉\]〕》\/／」』}]', '', corporate_name)

    return (company_name, corporate_name, corporate_sup)
    

#10, 「町域以下」のスクリーニング。230711
def town_scr_fun(contact_town):
#     screening_key_word = '(\(|（|)|）|人事|TEL|tel|Tel|ＴＥＬ|ｔｅｌ|Ｔｅｌ|本社|総務|人事|採用|管理|担当|新卒|学生|その他|営業所：|支店：|：|:|\/|／|※|【|〔|\[|＜|<|《|〈|{|［|\||〒|■|□|◇|◆|★|●|○|◎|･|・|『|「).*'
    screening_key_word = '(\\(|（|\\)|）|人事|TEL|tel|Tel|ＴＥＬ|ｔｅｌ|Ｔｅｌ|本社|総務|人事|採用|管理|担当|新卒|学生|その他|営業所：|支店：|：|:|\/|／|※|【|〔|\\[|＜|<|《|〈|{|［|\\||〒|■|□|◇|◆|★|●|○|◎|･|・|『|「|、).*'
    town_screeninged =re.sub(screening_key_word, '', contact_town)
    
    return town_screeninged



##ここまでは定義


#=======================================================
#第二ブロック 分割ファイルを読み込み、リスト型で抽出する。

#2. 求人詳細URLを取得。次のページへ進み、全件取得する。
#2-1.サイトのベースとなるURLを変数に入れる。


#6-2, ec2起動開始のメール送信。211221z
# 以下にGmailの設定を書き込む★ --- (*1)
gmail_account = "bhmarketing96010@gmail.com"
#二段階認証に変更。211027
gmail_password = "krsvljvzbqwaflgl"
# メールの送信先★ --- (*2)
mail_to = "baklis@blueheats.com"

# メールデータ(MIME)の作成 --- (*3)
# msj = logger.info(media_name + "の収集が完了しました。")
# subject = msj

#もしlogger内容でメール送信できなければ、↓に変更する。
now = datetime.datetime.now()
now_time = f"{now:%Y-%m-%d %H:%M:%S}"
subject = now_time + '【' + file_media_name + '_'+ str(sep_num) + "】のec2が起動しました。"

#本文はブランクでOK。211210
body = file_media_name + '_'+ str(sep_num) + "のec2が起動しました。"

msg = MIMEText(body, "html")
msg["Subject"] = subject
msg["To"] = mail_to
msg["From"] = gmail_account

# Gmailに接続 --- (*4)
server = smtplib.SMTP_SSL("smtp.gmail.com", 465,
    context=ssl.create_default_context())
server.login(gmail_account, gmail_password)
server.send_message(msg) # メールの送信
# print("メール送信 complete.")
logger.info("メール送信 complete.")



mynavi_base_url_1 = 'https://tenshoku.mynavi.jp/list/pg'
mynavi_base_url_2 = '/?jobsearchType=14&searchType=18'

page_count = 1

#ログ用のナンバー
pre_num = 0

#合計求人数を取得するために、一度アクセス。
mynavi_employment_list_url = mynavi_base_url_1 + str(page_count) + mynavi_base_url_2


#ここに5回ループ入れる。230611
#スピードアップのため5→4→3 へ変更。220908
for _ in range(10):
    try:
        driver.get(mynavi_employment_list_url)
        #ここで落ちるっぽいので追記。220729
        time.sleep(1)
    except TimeoutException as e:
        logger.info("タイムアウトしました。リトライします。")
        #以下追記。220805
        driver.quit()
        driver = webdriver.Firefox(options=options)
        time.sleep(2)
        driver.set_window_size(500, 500)
        # pass  # 失敗時はスルーする。
        pass
    #追加。220630
    except WebDriverException:
        logger.info('エラー：WebDriverException')
        #以下追記。220805
        driver.quit()
        driver = webdriver.Firefox(options=options)
        time.sleep(2)
        driver.set_window_size(500, 500)
        #pass
        pass
    except InvalidSessionIdException:
        logger.info('エラー：InvalidSessionIdException')
        #pass
        pass
    else:
        break  # 失敗しなかった時はループを抜ける


#2-2.合計求人件数を取得
total_offer_number = driver.find_element(By.CSS_SELECTOR,'.result__num em')
total_offer_number = total_offer_number.text
logger.info('\n' + '【マイナビの合計求人件数は、' + str(total_offer_number) + '件です】' + '\n')

#2-3-1.◯○件分の求人詳細URL, ベース広告プランを入れる空のリストを作っておく。
offer_employment_url_li = []
advertising_plan_li = []

#＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝

# #dodalike分割ロジック。220528
# #8,000分割。220528
# #page_countの自動切り替え
# #160→180。220729
# if int(sep_num) == 1:
#     page_count = 1
#     to_page_count = 280
# elif int(sep_num) == 2:
#     page_count = 281
#     to_page_count = int(total_offer_number) / 50 + 1

# ---

#新ロジック。241022
page_count_num = 200
collect_num = page_count_num * 50

if int(sep_num) == 1:
    page_count = 1
    to_page_count = page_count_num
elif int(sep_num) == 2:
    page_count = page_count_num * (int(sep_num) - 1) + 1
    to_page_count = page_count_num * int(sep_num)
elif int(sep_num) == 3:
    page_count = page_count_num * (int(sep_num) - 1) + 1
    to_page_count = int(total_offer_number) / 50 + 1



logger.info('\n' + '【page_countは' + str(page_count) + 'です】' + '\n')
logger.info('\n' + '【to_page_countは' + str(to_page_count) + 'です】' + '\n')


#＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝


#2-4-1.○○件分のURLを取得する
#切り上げ処理
#本番用
# while page_count <= int(total_offer_number) / 50 + 1:
    
#↓dodaライク本番用。220528
while page_count <= to_page_count:
    
#練習用
# while page_count <= 1:
    #2-4-2.求人一覧ページにアクセスs
    mynavi_employment_list_url = mynavi_base_url_1 + str(page_count) + mynavi_base_url_2
    #210108サーバーメンテの影響か、ここで落ちたので追加

    #page crash起きたので、1.5→3→1.5→3へ変更。220513
    time.sleep(1)
    driver.get(mynavi_employment_list_url)
    # time.sleep(0.7)

    #2-4-3.recomend○件分の求人詳細URLを取得し、リストに突っ込む。
    offer_employment_url_element_li = driver.find_elements(By.CSS_SELECTOR,'.cassetteRecruitRecommend__bottom .linkArrowS')
    for offer_employment_url_element in offer_employment_url_element_li:
        offer_employment_url = offer_employment_url_element.get_attribute('href')
        offer_employment_url = offer_employment_url.replace('msg/', '')     
        offer_employment_url_li.append(offer_employment_url)
        # logger.info(offer_employment_url)

    #2-4-4.recomend以外○件分の求人詳細URLを取得し、リストに突っ込む。
    offer_employment_url_element_li_2 = driver.find_elements(By.CSS_SELECTOR,'.cassetteRecruit__bottom .linkArrowS')
    for offer_employment_url_element_2 in offer_employment_url_element_li_2:
        offer_employment_url = offer_employment_url_element_2.get_attribute('href')
        offer_employment_url = offer_employment_url.replace('msg/', '')    
        offer_employment_url_li.append(offer_employment_url)    
        # logger.info(offer_employment_url)


    #2-4-5. recomend○件分のcassette要素を取得
    cassette_element_li = driver.find_elements(By.CSS_SELECTOR,'.cassetteRecruitRecommend')
    for cassette_element in cassette_element_li:
        advertising_plan = 'MT-A'
        advertising_plan_li.append(advertising_plan)
        # logger.info(advertising_plan)
    
    #2-4-6. recomend○件分以外のcassette要素を取得
    cassette_element_li_2 = driver.find_elements(By.CSS_SELECTOR,'.cassetteRecruit__content')
    for cassette_element_2 in cassette_element_li_2:
        case_rec_main = cassette_element_2.find_element(By.CSS_SELECTOR,'.cassetteRecruit__detail > div')
        case_rec_main = case_rec_main.get_attribute("class")
        if case_rec_main == 'cassetteRecruit__main':
        #MT-Sの判断は詳細画面の"メッセージタブ"でやる。
            advertising_plan = 'MT-A'
        elif case_rec_main == 'cassetteRecruit__mainM':
            advertising_plan = 'MT-B'
        elif case_rec_main == 'cassetteRecruit__mainL':
            advertising_plan = 'MT-C'
        elif case_rec_main == 'cassetteRecruit__mainLL':
            advertising_plan = 'MT-D'
        advertising_plan_li.append(advertising_plan)
        # logger.info(advertising_plan)

    pre_num += 50
    if pre_num % 200 == 0:
        logger.info('\n' + '【' + str(pre_num) + '件のデータ取得完了' + '】' + '\n')
        
    #メモリ不足対策 1000→50→3000件に一度リフレッシュ 220616
    #都度行う、へ変更。220520
    if pre_num % 3000 == 0:
        #closeを削除。220616
        # driver.close()
        driver.quit()
        driver = webdriver.Firefox(options=options)
        # time.sleep(5)


    #次のページへ繰る。
    page_count += 1

#2-5. URLとベースプランを入れる辞書を作る。
url_plan_dic = {}
url_plan_dic.update(zip(offer_employment_url_li, advertising_plan_li))



# #辞書型をスライス。230611＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊
# import itertools

# start = 0
# stop = 2
# sliced_dict = dict(itertools.islice(url_plan_dic.items(), start, stop))
# print(len(sliced_dict))  # {'b': 2, 'c': 3}

# url_plan_dic = sliced_dict

# #辞書型をスライス。230611＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊



dic_figs = len(url_plan_dic)
logger.info('\n' + '【マイナビの取得url数は、' + str(dic_figs) + '件です】' + '\n')


#2-6.エラー対策で、urlをcsvで出力。210120追記
df_my_url = pd.DataFrame(list(url_plan_dic.items()),columns=['url', 'ad_plan'])


today = datetime.datetime.today()
url_file_name = '{0:%y%m%d%H%M}'.format(today)+ file_media_name + 'temporary_urls.csv'

df_my_url.to_csv(output_path + '{0}'.format(url_file_name))


t2 = time.time()
elapsed_time = t2-t1
logger.info(f"経過時間：{elapsed_time}")


#=====================================================================
#ここから第三ブロック　データ収集、保存。更新210902

t3 = time.time() 

# #従業員数レンジのマスターの定義。210627
ran_1 = '(1) ～50人未満'
ran_2 = '(2) 50～100人未満'
ran_3 = '(3) 100～300人未満'
ran_4 = '(4) 300～500人未満'
ran_5 = '(5) 500～1000人未満'
ran_6 = '(6) 1000～3000人未満'
ran_7 = '(7) 3000～5000人未満'
ran_8 = '(8) 5000人以上'

#資本金レンジのマスターの定義。210830
cap_ran_1 = '(1) 750万円未満'
cap_ran_2 = '(2) 750万円以上1500万円未満'
cap_ran_3 = '(3) 1500万円以上3000万円未満'
cap_ran_4 = '(4) 3000万円以上5000万円未満'
cap_ran_5 = '(5) 5000万円以上1億円未満'
cap_ran_6 = '(6) 1億円以上5億円未満'
cap_ran_7 = '(7) 5億以上10億円未満'
cap_ran_8 = '(8) 10億円以上'

#売上高レンジのマスターの定義。220324
sales_ran_1 = '(1) 3億円未満'
sales_ran_2 = '(2) 3億円以上10億円未満'
sales_ran_3 = '(3) 10億円以上50億円未満'
sales_ran_4 = '(4) 50億円以上100万円未満'
sales_ran_5 = '(5) 100億円以上300億円未満'
sales_ran_6 = '(6) 300億円以上500億円未満'
sales_ran_7 = '(7) 500億以上1,000億円未満'
sales_ran_8 = '(8) 1,000億円以上'


#取得した件数を格納する変数を定義
num = 1


#6-2, 収集開始のメール送信。211210
# # 以下にGmailの設定を書き込む★ --- (*1)
# gmail_account = "bhmarketing96010@gmail.com"
# #二段階認証に変更。211027
# gmail_password = "krsvljvzbqwaflgl"
# # メールの送信先★ --- (*2)
# mail_to = "baklis@blueheats.com"

# メールデータ(MIME)の作成 --- (*3)
# msj = logger.info(media_name + "の収集が完了しました。")
# subject = msj

#もしlogger内容でメール送信できなければ、↓に変更する。
now = datetime.datetime.now()
now_time = f"{now:%Y-%m-%d %H:%M:%S}"
subject = now_time + '【' + file_media_name  + '_' + sep_num + "】の収集を開始します。"

#本文はブランクでOK。211210
body = file_media_name + '_'+ str(sep_num) + "の収集を開始します。"

msg = MIMEText(body, "html")
msg["Subject"] = subject
msg["To"] = mail_to
msg["From"] = gmail_account

# Gmailに接続 --- (*4)
server = smtplib.SMTP_SSL("smtp.gmail.com", 465,
    context=ssl.create_default_context())
server.login(gmail_account, gmail_password)
server.send_message(msg) # メールの送信
# print("メール送信 complete.")
logger.info("メール送信 complete.")


#4. 2で取得した求人詳細URLリストをforで回し、データ取得する。
for url, advertising_plan in url_plan_dic.items():
    for _ in range(5):  # 最大3回実行。リクナビには未実装。201019
        try:
            #210108サーバーメンテを考慮し、0.7→2へ変更
            # 210122前回遅すぎたので、2→1.2へ変更
            #三次開発に伴い、1.2→1→0.9→0.8へ変更。210924
            time.sleep(0.8)
            logger.info(url)
 
            driver.get(url)  # 失敗しそうな処理
        except TimeoutException as e:
            logger.info("タイムアウトしました。リトライします。")
            # pass  # 失敗時はスルーする。
            continue
        else:
            break  # 失敗しなかった時はループを抜ける
    else:
    #     raise TimeoutException("タイムアウトエラー")
        pass  # リトライが全部失敗した時はスルーする。


    #エラー例外処理のための try 
    try:
    # 4-0,前原稿の変数を全てクリア 201201
        publication_period = ''
        publication_start = ''
        information_updated = ''
        publication_end = ''
        occupation_major = ''
        occupation_medium = ''
        occupation_minor = ''
        company_name_original = ''
        occupation_type = ''
        company_name = ''
        corporate_name = ''
        corporate_sup = ''
        company_business = ''
        company_location = ''
        company_industry = ''
        company_employees = ''
        capital_stock = ''
        company_sales = ''
        company_establishment = ''
        work_location = ''
        salary = ''
        work_hours = ''
        welfare = ''
        holiday = ''
        job_description = ''
        application_conditions = ''
        employment_status = ''
        phone_number = ''
        phone_number_nonehyphen = ''
        mail_address = ''
        postal_code = ''
        street_address = ''
        charge_person = ''
        recruitment_background = ''
        contact_prefecture = ''
        contact_city  = ''
        contact_town = ''
#         advertising_plan = ''
        publication_url = ''
        applicant_id = ''
        company_id = ''
        corporate_url = ''
        company_employees_range = ''
        inexperienced_flag = ''
        #追加。210826
        public_offering = ''
        no_transfer = ''
        temp_staffing = ''
        establishment_num = ''
        stock_range = ''
        salary_class = ''
        lower_salary = ''
        upper_salary = ''
        english_skill = ''
        foreigner_activity = ''
        closing_month= ''
        sales_range = ''
        
        
        #4-0. today
        now = datetime.datetime.now()
        today = "{:%Y/%m/%d}".format(now)

        media_name = 'マイナビ転職'


        # 4-1,掲載期間・掲載開始日・掲載終了日の取得
        information_date = driver.find_element(By.CSS_SELECTOR,'.cassetteOfferRecapitulate .cassetteOfferRecapitulate__date')
        if information_date:
            information_date = information_date.text

        publication_period = ''
        publication_start = ''
        information_updated = re.search(r'(?<=情報更新日：)([0-9\/]*)', information_date)
        if information_updated:
            information_updated = information_updated.group()
            information_updated = datetime.datetime.strptime(information_updated, '%Y/%m/%d')
            information_updated = f"{information_updated:%Y/%m/%d}"

            publication_end = re.search(r'(?<=掲載終了予定日：)([0-9\/]*)', information_date)
            publication_end = publication_end.group()
            #以下2022/3/1→2022/03/01に修正スクリプト。（do,riku,ecr,toraのみ）220320
            publication_end = datetime.datetime.strptime(publication_end, '%Y/%m/%d')
            publication_end = f"{publication_end:%Y/%m/%d}"


        # 4-2,掲載職種大分類・中分類・小分類
        occupation_major = driver.find_element(By.CSS_SELECTOR,'.breadcrumb__list .breadcrumb__item:nth-of-type(3) .breadcrumb__link')
        occupation_major = occupation_major.text
        occupation_medium = driver.find_element(By.CSS_SELECTOR,'.breadcrumb__list .breadcrumb__item:nth-of-type(4) .breadcrumb__link')
        occupation_medium = occupation_medium.text
        occupation_minor = driver.find_element(By.CSS_SELECTOR,'.breadcrumb__list .breadcrumb__item:nth-of-type(5) .breadcrumb__link')
        occupation_minor = occupation_minor.text


        #4-3. 掲載社名
        company_name_original = driver.find_element(By.CSS_SELECTOR,'.blockWrapper .rightBlock .companyName')
        company_name_original_2 = driver.find_element(By.CSS_SELECTOR,'.blockWrapper .rightBlock .companyNameAdd')
        company_name_original = company_name_original.text + ' ' + company_name_original_2.text
        logger.info(company_name_original)

        # # 4-4,媒体記載職種
        occupation_type = driver.find_element(By.CSS_SELECTOR,'.blockWrapper .rightBlock .occName')
        occupation_type = occupation_type.text



        # 4-5,社名・事業内容・事業所・従業員数・業種・資本金・売上高・設立年・代表者・企業HP
        #通常原稿
        #    if check_exists_element('.descWriterSet--icon'):
        company_content_li = driver.find_elements(By.CSS_SELECTOR,'.thL tr')


        #thが○○の時、tdを抜き取る、と言うスクリプトを書く
        #company_nameは別途取得
        #宣言文
        # company_name = company_name_original
        company_location = ''
        for company_content in company_content_li:
            th_text = company_content.find_element(By.CSS_SELECTOR,'th')
            th_text = th_text.text
            td_text = company_content.find_element(By.CSS_SELECTOR,'td')
            td_text = td_text.text    
            if th_text == '事業内容':
                company_business = td_text
                company_business = company_business.replace('\n', '')
            elif '本社所在地' in th_text:
                company_location_origin = td_text
                company_location = company_location_origin.replace('\n', '')
            elif th_text == '従業員数':
                company_employees = td_text
                company_employees = company_employees.replace('\n', '')
                # logger.info(company_employees)
                
            elif th_text == '資本金':
                capital_stock = td_text
                capital_stock = capital_stock.replace('\n', '')                  
            elif th_text == '売上高':
                company_sales = td_text
                company_sales = company_sales.replace('\n', '')
            elif th_text == '設立':
                company_establishment = td_text
                company_establishment = company_establishment.replace('\n', '')                             
            elif th_text == '企業ホームページ':
                corporate_url = td_text
                #HP欄は自由記述形式だったので、正規表現導入。211030
                corporate_url = re.search(r'https?:\/\/[\w/:%#\$&\?\(\)~\.=\+\-]+', corporate_url)
                if corporate_url:
                    corporate_url = corporate_url.group()
                # logger.info(corporate_url)


        #4-5-2. 業種をforで回し取得する。
        search_list_li = driver.find_elements(By.CSS_SELECTOR,'.card__content .searchResultTable tr')

        for search_list in search_list_li:
                th_text = search_list.find_element(By.CSS_SELECTOR,'th')
                th_text = th_text.text
                td_text = search_list.find_element(By.CSS_SELECTOR,'td')
                td_text = td_text.text
                if th_text == '業種':
                    company_industry = td_text


        #4-6,勤務地・給与・勤務時間・待遇福利厚生・休日休暇・仕事内容・求めている人材・募集背景
        application_guideline_li = driver.find_element(By.CSS_SELECTOR,'.jobPointArea__mainWrap .jobOfferTable tbody')
        application_guideline_li = application_guideline_li.find_elements(By.CSS_SELECTOR,'tr')
        for application_guideline in application_guideline_li:
            th_text = application_guideline.find_element(By.CSS_SELECTOR,'th')
            th_text = th_text.text
            td_text = application_guideline.find_element(By.CSS_SELECTOR,'td')
            td_text = td_text.text
            if th_text == '勤務地':
                work_location = td_text
                work_location = work_location.replace('\n', '')
    #             logger.info(work_location)
            elif th_text == '給与':
                salary = td_text
                salary = salary.replace('\n', '')                    
    #             logger.info(salary)
            elif th_text == '勤務時間':
                work_hours = td_text
                work_hours = work_hours.replace('\n', '')                
    #             logger.info(work_hours)
            elif th_text == '福利厚生':
                welfare = td_text
                welfare = welfare.replace('\n', '')                    
    #             logger.info(welfare)
            elif th_text == '休日・休暇':
                holiday = td_text
                holiday = holiday.replace('\n', '')                                        
    #             logger.info(holiday)
            elif th_text == '雇用形態':
                employment_status = td_text
                employment_status = employment_status.replace('\n', '')                                        
    #             logger.info(employment_status)

        job_description = driver.find_element(By.CSS_SELECTOR,'.jobPointArea__wrap-jobDescription')
        job_description = job_description.text
        job_description = job_description.replace('\n', '')

        application_conditions = driver.find_element(By.CSS_SELECTOR,'#jobInfo2')
        application_conditions = application_conditions.text
        application_conditions_2 = driver.find_element(By.CSS_SELECTOR,'#parts_target_person + .jobPointArea__head')
        application_conditions_2 = application_conditions_2.text
        application_conditions_3 = driver.find_element(By.CSS_SELECTOR,'.jobPointArea__body--large')
        application_conditions_3 = application_conditions_3.text
        application_conditions = application_conditions + application_conditions_2 + application_conditions_3
        application_conditions = application_conditions.replace('\n', '')

        recruitment_background = driver.find_element(By.CSS_SELECTOR,'.jobPointArea__body-prArea')
        recruitment_background = recruitment_background.text
        recruitment_background = recruitment_background.replace('\n', '')


        #4-8. 電話番号・電話番号（ハイフンなし）・メールアドレス・郵便番号・連絡先住所・担当者

        information_tr_li = driver.find_elements(By.CSS_SELECTOR,'.jobOfferTable-howToApply > tbody > tr')
        for information_tr in information_tr_li:
            th_text = information_tr.find_element(By.CSS_SELECTOR,'th')
            th_text = th_text.text
            td_text = information_tr.find_element(By.CSS_SELECTOR,'td')
            td_text = td_text.text
            if th_text == '問い合わせ':
        #         logger.info(td_text)
                company_name = information_tr.find_element(By.CSS_SELECTOR,'.jobOfferTable__body .textBold')
                company_name = company_name.text
                # logger.info('社名：' + company_name)

                #法人名を抽出する独自関数。230129
                x = gen_cor_name(company_name)
                company_name = x[0]
                corporate_name = x[1]
                corporate_sup = x[2]


#=========================================
#以下高速版 201206
                postal_code = re.search(r'〒+\s?\d{3}-\d{4}', td_text)
                if not postal_code:
                    postal_code = ''
                else:
                    postal_code = postal_code.group().replace('〒','').replace(' ', '')

                #ここに移動。230714『ケ』→『ヶ』に統一。pattern_text.py, complement_pref.pyは全て『ヶ』に修正済み。.replaceはブランクを無視する。220906
                td_text = td_text.replace('ケ', 'ヶ')
                street_address = re.search(pat, td_text)
                if not street_address:
                    #都道府県の記載がなく、市区町村から始まる場合の処理
                    street_address = re.search(city_pat, td_text)
                    if not street_address:
                        street_address = ''
                    else:
                        street_address = street_address.group()
                else:
                    street_address = street_address.group()
                #         logger.info(postal_code)
                #         logger.info(street_address)


                charge_person = re.search(r'(?<=採用担当\n)(.+)(?!=\n)', td_text)
                if not charge_person:
                    charge_person = ''
                else:
                    charge_person = charge_person.group()

#                 #電話番号取得ロジックの改善テスト。221109
#                 phone_number = re.search(r'0\d{1,3}[-ｰーーーｰ‐－（()）]\d{2,4}[-ｰーーーｰ‐－（()）]\d{3,4}', td_text)
#                 if not phone_number:
#                     phone_number = ''
#                     phone_number_nonehyphen = ''
#                 else:
#                     phone_number = phone_number.group()
#                     # phone_number_nonehyphen = phone_number.replace('-', '')
#                     #電話番号取得ロジックの改善テスト。221109
#                     phone_number_nonehyphen = re.sub(r'[-ｰーーーｰ‐－]', '', phone_number)
# #                         phone_number_nonehyphen = '=' + '\"' + phone_number_nonehyphen + '\"'        

                #独自関数に変更。230105
                x = gen_phone_num(td_text)
                phone_number = x[0]
                phone_number_nonehyphen = x[1]

                # #半角に修正してからメールアドレス取得ロジックでテスト。221109
                # td_text_normal = unicodedata.normalize("NFKC", td_text)
                # mail_address = re.search(r'[a-zA-Z0-9\.\-_+]+@[\w\.-]+\.[a-zA-Z]{2,}', td_text_normal)
                # if not mail_address:
                #     mail_address = ''
                # else:
                #     mail_address = mail_address.group()
                # # logger.info(mail_address)

                #独自関数に変更。230105
                mail_address = gen_mail_ad(td_text)

            # 4-9,募集背景は取得済み

            
        #人材紹介判別ロジック移動。221112
#         if 'マイナビエージェント' in charge_person or 'マイナビ転職キャリアパートナー' in charge_person:
        #『マイナビ転職キャリアパートナー』は直販の人材案件で、既得権外なので判別したい。水谷さん。220421
        if 'キャリアパートナー' in charge_person:
            advertising_plan = advertising_plan + '_agent_cp'

        if 'マイナビエージェント' in charge_person:
            advertising_plan = advertising_plan + '_agent'

        # #広告プランの先頭に媒体名の見出しつける。220405
        # advertising_plan = 'my_' + advertising_plan
        
        print(advertising_plan)
            

        # 4-10,お問い合わせ先/郵便番号・都道府県・市区町村・町域・ビル名※郵便番号は↑で取得済み
        if not street_address:
            contact_prefecture = ''
            contact_city = ''
            contact_town = ''        
        else:
            # #『ケ』→『ヶ』に統一。pattern_text.py, complement_pref.pyは全て『ヶ』に修正済み。.replaceはブランクを無視する。220906
            # street_address = street_address.replace('ケ', 'ヶ')
            #谷さんオリジナルモジュールをインポート。201031
            import pattern_text as pt
            pat = pt.get_pattern_text()
            match = re.search(pat, street_address)
            if not match:
                contact_prefecture = ''
                contact_city = ''
                contact_town = ''
            else:
                contact_prefecture = match.group(1) or ''
                contact_city = match.group(2) or ''
                contact_town = match.group(3) or ''

            #「町域以下」精査する。230711
            contact_town = town_scr_fun(contact_town)
                
########################ここに『cp or 『採用担当』欄に「マイナビ転職CP内」の場合、『本社住所』から取得』処理を追記。221112
        charge_person_no_space = charge_person.replace(' ', '')
    
        #『広告プラン』が「agent_cp」の場合、『お問い合わせ先』を『本社住所』から取得する。221112
        # if 'agent_cp' in advertising_plan or 'CP内' in charge_person_no_space:
        #『キャリアパートナー内』を追加。
        # if 'agent_cp' in advertising_plan or 'CP内' in charge_person_no_space or 'キャリアパートナー内' in charge_person_no_space:
        #「agent_cp」→「agent」へ変更。230712
        if 'agent' in advertising_plan or 'CP内' in charge_person_no_space or 'キャリアパートナー内' in charge_person_no_space:
            #『ケ』→『ヶ』に統一。pattern_text.py, complement_pref.pyは全て『ヶ』に修正済み。.replaceはブランクを無視する。220906
#             company_location = company_location.replace('ケ', 'ヶ')
            company_location_origin = company_location_origin.replace('ケ', 'ヶ')
            
            #谷さんオリジナルモジュールをインポート。201031
            import pattern_text as pt
            pat = pt.get_pattern_text()
            match = re.search(pat, company_location_origin)
            if not match:
                contact_prefecture = ''
                contact_city = ''
                contact_town = ''
            else:
                contact_prefecture = match.group(1) or ''
                contact_city = match.group(2) or ''
                contact_town = match.group(3) or ''

            #「町域以下」精査する。230711
            contact_town = town_scr_fun(contact_town)

            #「お問合せ住所」と「お問合せ都道府県」などを一致させるため、「郵便番号」を削除しておく。230711
            postal_code = ''
    

        #都道府県がブランク、かつ市区町村が存在する場合、都道府県補完モジュール発動。220324
        if not contact_prefecture and contact_city:
            contact_prefecture = cp.get_complement_pref(contact_city)
            
        #「お問合せ住所」と「お問合せ都道府県」などを一致させる。230711
        street_address = contact_prefecture + contact_city + contact_town


        #     # 4-11,広告プラン
        #MT-SとMT-Aの判別をする。（『メッセージ』タブがあれば、'MT-S'へ上書きする。
        #『経営者メッセージ』の場合に反応してしまうエラー改善。220412

#         element = driver.find_element(By.CSS_SELECTOR,'.tabNaviRecruit__list')
#         element_text = element.text
#         if 'メッセージ' in element_text:
#             advertising_plan = 'MT-S'
        tab_element_li = driver.find_elements(By.CSS_SELECTOR,'.tabNaviRecruit__list li')
        for tab_element in tab_element_li:
            element_text = tab_element.text
            if element_text == 'メッセージ':
                advertising_plan = 'MT-S'

        #広告プランの先頭に媒体名の見出しつける。220405
        #MT-Sだけ『my_』つけ漏れ。ここに移動。221213
        advertising_plan = 'my_' + advertising_plan

#         #210120 人材業界判別ロジック追記
# #         if 'マイナビエージェント' in charge_person or 'マイナビ転職キャリアパートナー' in charge_person:
#         #『マイナビ転職キャリアパートナー』は直販の人材案件で、既得権外なので判別したい。水谷さん。220421
#         if 'キャリアパートナー' in charge_person:
#             advertising_plan = advertising_plan + '_agent_cp'

#         if 'マイナビエージェント' in charge_person:
#             advertising_plan = advertising_plan + '_agent'

#         #広告プランの先頭に媒体名の見出しつける。220405
#         advertising_plan = 'my_' + advertising_plan
        
#         print(advertising_plan)
            
        #従業員数レンジを下部に追加。210830
        if company_employees:
            #従業員数レンジを修正。210721
            com_em_ran = company_employees.replace(',', '').replace(' ', '').replace('，', '').replace('.', '')
            #『人』or『名』より前を抜き出す。『万』も含めて
#             company_employees_range = re.search(r'[\d|万]+(?=\D)',company_employees_range)
            #『万か数字』を含み、『名か人』までの判別。
            company_employees_range = re.search(r'[\d|万]+(?=[名|人])', com_em_ran)
            #『万か数字』を含み、『名か人』までが無い場合。                
            if not company_employees_range:
                #『万か数字』を含み、数字以外までの場合。
                company_employees_range = re.search(r'[\d|万]+(?!=\d)', com_em_ran)
                #『万か数字』を含み、数字以外までが無いの場合。
                if not company_employees_range:
                    company_employees_range = ''
                else:
                    #『万か数字』を含み、数字以外までがある場合。
                    company_employees_range = company_employees_range.group()
                    #『万』が含まれる場合の処理
                    if '万' in company_employees_range:
                        vcm_int = int('10000')
                    else:         
                        vcm_int = company_employees_range
                        vcm_int = int(vcm_int)
            #『万か数字』を含み、『名か人』までがある場合。
            else:
                company_employees_range = company_employees_range.group()
                #『万』が含まれる場合の処理
                if '万' in company_employees_range:
                    vcm_int = int('10000')
                else:         
                    vcm_int = company_employees_range
                    vcm_int = int(vcm_int)

            if 5000 <= vcm_int:
                company_employees_range = ran_8
            if 3000 <= vcm_int < 5000:
                company_employees_range = ran_7
            if 1000 <= vcm_int < 3000:
                company_employees_range = ran_6
            if 500 <= vcm_int < 1000:
                company_employees_range = ran_5
            if 300 <= vcm_int < 500:
                company_employees_range = ran_4
            if 100 <= vcm_int < 300:
                company_employees_range = ran_3
            if 50 <= vcm_int < 100:
                company_employees_range = ran_2
            if vcm_int < 50:
                company_employees_range = ran_1
#             logger.info(company_employees_range)


        #4-8-2. 未経験フラグ追加。210628
        inexperienced_ele = driver.find_element(By.CSS_SELECTOR,'.cassetteRecruit__attribute.cassetteRecruit__attribute-jobinfo')
        inexperienced_text = inexperienced_ele.text

        if '職種未経験' in inexperienced_text or '職種・業種未経験' in inexperienced_text:
            inexperienced_flag = '有'
        else:
            inexperienced_flag = '無'
        # logger.info(inexperienced_flag)

        #株式公開フラグの取得。210830
        if '上場' in inexperienced_text:
            public_offering = '有'
        else:
            public_offering = '無'
#                 logger.info(public_offering)

        #転勤なしフラグの取得。210830
        if '転勤なし' in inexperienced_text:
            no_transfer = '有'
        else:
            no_transfer = '無'
#                 logger.info(no_transfer)


        #設立年数値、下部に追加。210830
        if company_establishment:
            company_establishment_2 = company_establishment.replace(',', '').replace('、', '')

            #西暦の場合の処理。
            establishment_range_check = re.search(r'\d{4}(?=\D)', company_establishment_2)
            if establishment_range_check:
                establishment_num = establishment_range_check.group()
                #↓これ入れ忘れてたから『文字列』になっていたぽい。220324
                establishment_num = int(establishment_num)
            else:
                #和暦の場合の処理。
                establishment_range_check = re.search(r'(\d+)|(元)(?=\D)', company_establishment_2)
                if establishment_range_check:
                    establishment_num = establishment_range_check.group()
                    establishment_num = establishment_num.replace('元', '1')
                    establishment_num = int(establishment_num)

                    # 明治 1868~1911(1912),大正1912~1925(1926),昭和1926~1988(1989),平成1989~2018,令和2019~
                    if '明治' in company_establishment_2:
                        establishment_num += 1867
                    elif '大正' in company_establishment_2:
                        establishment_num += 1911
                    elif '昭和' in company_establishment_2:
                        establishment_num += 1925
                    elif '平成' in company_establishment_2:
                        establishment_num += 1988
                    elif '令和' in company_establishment_2:
                        establishment_num += 2018
                #ブランク、もしくは変換不可能な場合の処理。
                else:
                    establishment_num = ''
                    
            #1000年以下はエラーと判断し、ブランク処理する。220405
            if establishment_num :
                if establishment_num <= 1000:
                    establishment_num = ''



        #資本金レンジ、下部に追加。210909
        if capital_stock:
            capital_stock_2 = capital_stock.replace(',', '').replace('、', '').replace(' ', '').replace('　', '')
            #非貪欲マッチで『円』まで『円』付きで抜き取る。『1,000万円（国内グループ計8億1,200万円）』のケースに対応。210906
            capital_stock_2 = re.search('.+?円', capital_stock_2)
            if capital_stock_2:
                capital_stock_2 = capital_stock_2.group()

                #小数点以下を削除する。210906
                if '.' in capital_stock_2:
                    capital_stock_2 = re.sub(r'\.(\d+)(?=\D)','', capital_stock_2)

                #『億』が含まれる場合の処理。
                #全て『万円』単位で処理する。
                if '億' in capital_stock_2:
                    capital_stock_num = re.search(r'(\d+)(?=億)', capital_stock_2)
                    if capital_stock_num:
                        capital_stock_num = capital_stock_num.group()
                        capital_stock_num = capital_stock_num + '0000'
                        capital_stock_int = int(capital_stock_num)
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        capital_stock_int = ''  

                elif '千万円' in capital_stock_2:
                    capital_stock_num = re.search(r'(\d+)(?=千万円)', capital_stock_2)
                    if capital_stock_num:
                        capital_stock_num = capital_stock_num.group()
                        capital_stock_num = capital_stock_num + '000'
                        capital_stock_int = int(capital_stock_num)
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        capital_stock_int = ''

                elif '百万円' in capital_stock_2:
                    capital_stock_num = re.search(r'(\d+)(?=百万円)', capital_stock_2)
                    if capital_stock_num:
                        capital_stock_num = capital_stock_num.group()
                        capital_stock_num = capital_stock_num + '00'
                        capital_stock_int = int(capital_stock_num)
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        capital_stock_int = ''

                elif '万' in capital_stock_2:
                    capital_stock_num = re.search(r'(\d+)(?=万)', capital_stock_2)
                    if capital_stock_num:
                        capital_stock_num = capital_stock_num.group()
                        capital_stock_int = int(capital_stock_num)
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        capital_stock_int = '' 

                elif '千円' in capital_stock_2:
                    capital_stock_num = re.search(r'(\d+)(?=千円)', capital_stock_2)
                    if capital_stock_num:
                        capital_stock_num = capital_stock_num.group()
                        capital_stock_int = int(capital_stock_num)
                        # 切り捨て
                        capital_stock_int = capital_stock_int // 10
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        capital_stock_int = '' 

                #『億』『万』がなく、『円』のみの時。
                elif '円' in capital_stock_2:
                    capital_stock_num = re.search(r'(\d+)(?=円)', capital_stock_2)
                    if capital_stock_num:
                        capital_stock_num = capital_stock_num.group()
                        #後方4桁の数字を削除し、単位を『万』に揃える。
                        capital_stock_num = re.sub(r'\d{4}$','', capital_stock_num)
                        if capital_stock_num:
                            capital_stock_int = int(capital_stock_num)
                        #金額の数値が3桁以下の場合で取得できない場合。
                        else:
                            capital_stock_int = ''
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        capital_stock_int = ''

                #ブランク、もしくは変換不可能な場合の処理。
                else:
                    capital_stock_int = ''

                #『資本金』の表記が想定外の場合、capital_stock_intがブランクになるので、エスケープ。210830 
                if capital_stock_int:
                    if capital_stock_int < 750:
                        stock_range = cap_ran_1
                    elif 750 <= capital_stock_int < 1500:
                        stock_range = cap_ran_2
                    elif 1500 <= capital_stock_int < 3000:
                        stock_range = cap_ran_3
                    elif 3000 <= capital_stock_int < 5000:
                        stock_range = cap_ran_4
                    elif 5000 <= capital_stock_int < 10000:
                        stock_range = cap_ran_5
                    elif 10000 <= capital_stock_int < 50000:
                        stock_range = cap_ran_6
                    elif 50000 <= capital_stock_int < 100000:
                        stock_range = cap_ran_7
                    elif 100000 <= capital_stock_int:
                        stock_range = cap_ran_8
                    else:
                        stock_range = ''

            # logger.info(capital_stock_int)
            # logger.info(stock_range)

            
        #派遣会社フラグ追加。210830
        if '派遣' in company_business:
            temp_staffing = '有'
        else:
            temp_staffing_check = re.search(r'\d{2}[-ー−ｰ－]\d{6}', company_business)
            if temp_staffing_check:
                temp_staffing = '有'
            else:
                temp_staffing = '無'
#                     logger.info(temp_staffing)
            
    
        # #給与レンジの取得。210830
        # if '初年度の年収' in salary:
        #     salary_rep = salary.replace(',', '').replace('、', '')
        #     salary_2 = re.search(r'(?<=初年度の)年収\d{3,4}万円～\d{3,4}万円', salary_rep)

    
#＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊

        #給与レンジ取得スクリプトの改修。230405
        salary_rep = salary.replace(',', '').replace('、', '')
        #マイナビは『初年度の年収』表記を優先して取得する。230403
        salary_check_ele = re.search('(初年度の年収).{0,12}\d{3,4}(万|～).{0,7}', salary_rep)

        if salary_check_ele:
            salary_check = salary_check_ele.group()
            lower_salary_check_ele = re.search('\d{3,4}(?=(万|～))', salary_check)
            if lower_salary_check_ele:
                lower_salary_check = lower_salary_check_ele.group()
                lower_salary = re.search(r'\d{3,4}', lower_salary_check)
                #念の為 ifでエスケープしとく。
                if lower_salary:
                    lower_salary = lower_salary.group()
                    #全角のエスケープ追記。220324
                    lower_salary = int(lower_salary)

            upper_salary_check_ele = re.search('(?<=～|~)\d{3,4}(?=万)', salary_check)
            #念の為 ifでエスケープしとく。
            if upper_salary_check_ele:
                upper_salary_check = upper_salary_check_ele.group()
                upper_salary = re.search(r'\d{3,4}', upper_salary_check)
                #念の為 ifでエスケープしとく。
                if upper_salary:
                    upper_salary = upper_salary.group()
                    #全角のエスケープ追記。220324
                    upper_salary = int(upper_salary)

        #給与下限も上限も取れなかった場合は、他のパラメーターも加えて再取得。230403
        else:
            salary_check_ele = re.search('((?<!半期)年俸|想定年収|初年度の?(想定|平均)?年収).{0,12}\d{3,4}(万|～).{0,7}', salary_rep)
            if salary_check_ele:
                salary_check = salary_check_ele.group()
                lower_salary_check_ele = re.search('\d{3,4}(?=(万|～))', salary_check)
                if lower_salary_check_ele:
                    lower_salary_check = lower_salary_check_ele.group()
                    lower_salary = re.search(r'\d{3,4}', lower_salary_check)
                    #念の為 ifでエスケープしとく。
                    if lower_salary:
                        lower_salary = lower_salary.group()
                        #全角のエスケープ追記。220324
                        lower_salary = int(lower_salary)

                upper_salary_check_ele = re.search('(?<=～|~)\d{3,4}(?=万)', salary_check)
                #念の為 ifでエスケープしとく。
                if upper_salary_check_ele:
                    upper_salary_check = upper_salary_check_ele.group()
                    upper_salary = re.search(r'\d{3,4}', upper_salary_check)
                    #念の為 ifでエスケープしとく。
                    if upper_salary:
                        upper_salary = upper_salary.group()
                        #全角のエスケープ追記。220324
                        upper_salary = int(upper_salary)

#＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊


    
        #英語スキルフラグ完成。210830
        if '英語' in job_description or '英語' in application_conditions or 'TOEIC' in application_conditions:
            english_skill = '有'
        else:
            english_skill = '無'

        #外国籍活躍フラグ完成。210830
        if '国籍' in job_description or '国籍' in application_conditions or '日本語' in application_conditions:
            foreigner_activity = '有'
        else:
            foreigner_activity = '無'

            
        #想定決算月の取得。220324
        if company_establishment:
            closing_month_ele = re.search(r'\d{1,2}月', company_establishment)
            if closing_month_ele:
                closing_month_p = closing_month_ele.group()
                closing_month_p = closing_month_p.replace('月', '')
                #int型に変更すれば、半角化する必要ない。220314
                closing_month = int(closing_month_p) -1
                if closing_month == 0:
                    closing_month = 12
            else:
                closing_month = ''

            #想定決算月が1~12以外の時、ブランク処理する。220405
            if closing_month:
                if not 1 <= closing_month <= 12:
                    closing_month = ''

                    
        #『売上高レンジ』220314
        #前求人の値をクリア。220319
        company_sales_int = ''
        if company_sales:
            if '円' in company_sales:
                company_sales_2 = company_sales.replace(',', '').replace('、', '').replace(' ', '').replace('　', '')
                #非貪欲マッチで『円』まで『円』付きで抜き取る。『1,000万円（国内グループ計8億1,200万円）』のケースに対応。210906
                company_sales_2 = re.search('.+?円', company_sales_2)
                if company_sales_2:
                    company_sales_2 = company_sales_2.group()
                else:
                    #『売上高』が『円(2020年度実績)』などで円より前の文字列がない場合の処理。220310
                    company_sales_2 = ''
                    company_sales_int = ''

                #小数点以下を削除する。210906
                if '.' in company_sales_2:
                    company_sales_2 = re.sub(r'\.(\d+)(?=\D)','', company_sales_2)

                #『億』が含まれる場合の処理。
                #全て『万円』単位で処理する。
                if '兆' in company_sales_2:
                    company_sales_num = re.search(r'(\d+)(?=兆)', company_sales_2)
                    if company_sales_num:
                        company_sales_num = company_sales_num.group()
                        company_sales_num = company_sales_num + '00000000'
                        company_sales_int = int(company_sales_num)
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        company_sales_int = ''  

                elif '千億円' in company_sales_2:
                    #logger.info('b')
                    company_sales_num = re.search(r'(\d+)(?=千億円)', company_sales_2)
                    if company_sales_num:
                        #logger.info('a')
                        company_sales_num = company_sales_num.group()
                        company_sales_num = company_sales_num + '0000000'
                        company_sales_int = int(company_sales_num)
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        company_sales_int = ''

                elif '百億円' in company_sales_2:
                    #logger.info('b')
                    company_sales_num = re.search(r'(\d+)(?=百億円)', company_sales_2)
                    if company_sales_num:
                        #logger.info('a')
                        company_sales_num = company_sales_num.group()
                        company_sales_num = company_sales_num + '000000'
                        company_sales_int = int(company_sales_num)
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        company_sales_int = ''

                #誤字も織り込む。220227
                elif '億' in company_sales_2 or '憶' in company_sales_2:
                    company_sales_num = re.search(r'(\d+)(?=億|憶)', company_sales_2)
                    if company_sales_num:
                        company_sales_num = company_sales_num.group()
                        company_sales_num = company_sales_num + '0000'
                        company_sales_int = int(company_sales_num)
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        company_sales_int = '' 

                elif '百万円' in company_sales_2:
                    company_sales_num = re.search(r'(\d+)(?=百万円)', company_sales_2)
                    if company_sales_num:
                        company_sales_num = company_sales_num.group()
                        company_sales_num = company_sales_num + '00'
                        company_sales_int = int(company_sales_num)
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        company_sales_int = '' 

                elif '万円' in company_sales_2:
                    company_sales_num = re.search(r'(\d+)(?=万円)', company_sales_2)
                    if company_sales_num:
                        company_sales_num = company_sales_num.group()
                        company_sales_int = int(company_sales_num)
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        company_sales_int = '' 

                elif '千円' in company_sales_2:
                    company_sales_num = re.search(r'(\d+)(?=千円)', company_sales_2)
                    if company_sales_num:
                        company_sales_num = company_sales_num.group()
                        company_sales_int = int(company_sales_num)
                        # 切り捨て
                        company_sales_int = company_sales_int // 10
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        company_sales_int = '' 

                #『兆』『億』『万』がなく、『円』のみの時。
                elif '円' in company_sales_2:
                    company_sales_num = re.search(r'(\d+)(?=円)', company_sales_2)
                    if company_sales_num:
                        company_sales_num = company_sales_num.group()
                        #後方4桁の数字を削除し、単位を『万』に揃える。
                        company_sales_num = re.sub(r'\d{4}$','', company_sales_num)
                        if company_sales_num:
                            company_sales_int = int(company_sales_num)
                        #金額の数値が3桁以下の場合で取得できない場合。
                        else:
                            company_sales_int = ''
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        company_sales_int = ''

                #ブランク、もしくは変換不可能な場合の処理。
                else:
                    company_sales_int = ''

            #『非上場』など円が入っていないケースはブランク処理。220227
            else:
                company_sales_int = ''

            #『売上高』の表記が想定外の場合、company_sales_intがブランクになるので、エスケープ。220227
            if company_sales_int:
                if company_sales_int < 30000:
                    sales_range = sales_ran_1
                elif 30000 <= company_sales_int < 100000:
                    sales_range = sales_ran_2
                elif 100000 <= company_sales_int < 500000:
                    sales_range = sales_ran_3
                elif 500000 <= company_sales_int < 1000000:
                    sales_range = sales_ran_4
                elif 1000000 <= company_sales_int < 3000000:
                    sales_range = sales_ran_5
                elif 3000000 <= company_sales_int < 5000000:
                    sales_range = sales_ran_6
                elif 5000000 <= company_sales_int < 10000000:
                    sales_range = sales_ran_7
                elif 10000000 <= company_sales_int:
                    sales_range = sales_ran_8
                else:
                    sales_range = ''
 
            
            
            
            
            
        # 4-12,掲載URL
        publication_url = url
    #     logger.info(publication_url)


        #4-13. 求人ID
        applicant_id =  re.search(r'(?<=jobinfo-)[\w-]+(?=/)', publication_url)
        applicant_id = applicant_id.group()

        #4-14. 企業ID
        company_id = re.search(r'(?<=jobinfo-)[\w]+(?=-)', publication_url)
        company_id = company_id.group()


        #4-15, 企業HP※取得済み


    #＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊
    #＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊

        #contact_prefectureがない場合（agent, 広告共通で）、company_locationから取得する。ただし「お問合せ住所」はデータが重くなるので反映させない。,230713
        if not contact_prefecture:

            #「本社住所」から取得する。230713
            company_location = company_location.replace('ケ', 'ヶ')
            #谷さんオリジナルモジュールをインポート。201031
            import pattern_text as pt
            pat = pt.get_pattern_text()
            match = re.search(pat, company_location)
            if not match:
                contact_prefecture = ''
                contact_city = ''
                contact_town = ''
            else:
                contact_prefecture = match.group(1) or ''
                contact_city = match.group(2) or ''
                contact_town = match.group(3) or ''

            #「町域以下」精査する。230711
            contact_town = town_scr_fun(contact_town)

            #都道府県がブランク、かつ市区町村が存在する場合、都道府県補完モジュール発動。220324
            if not contact_prefecture and contact_city:
                contact_prefecture = cp.get_complement_pref(contact_city)

            #郵便番号をクリアにする。230715
            postal_code = ''


    #＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊
    #＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊

        #4-16, python3.8用に修正。230608
        heading_columns_variable = [[applicant_id, company_id, today, media_name, company_name, corporate_name, corporate_sup,
                                                            phone_number, phone_number_nonehyphen, publication_period, publication_start, information_updated,  publication_end,
                                                            occupation_major, occupation_medium, occupation_minor, company_name_original,
                                                            occupation_type, company_business, company_location, company_industry, company_employees, capital_stock, company_sales,
                                                            company_establishment, work_location, salary, work_hours, welfare, holiday, job_description, application_conditions, employment_status, 
                                                            mail_address, postal_code, street_address, charge_person,
                                                            recruitment_background, contact_prefecture, contact_city , contact_town,
                                                            advertising_plan, publication_url, corporate_url, company_employees_range, inexperienced_flag, 
                                                            no_transfer, establishment_num, public_offering, stock_range, temp_staffing, salary_class, lower_salary, 
                                                            upper_salary, english_skill, foreigner_activity, closing_month, sales_range]]
        df_part = pd.DataFrame(heading_columns_variable, columns=heading_columns)
        df_info = pd.concat([df_info, df_part], ignore_index=True)


   #4-15. 例外処理パターンを追記。201122
    except NoSuchElementException:
        logger.info('エラー：NoSuchElementException')
        pass

    #例外が発生したら、その時までに取得していたデータを書き出す処理を追記。201122
    except TimeoutException:
        logger.info('エラー：TimeoutException')
        #5. CSVに吐き出す。
        today = datetime.datetime.today()
        media_name = 'disruption_' + file_media_name
        file_name = '{0:%y%m%d%H%M}'.format(today)+media_name + '.csv'
        # , index = False 追加 210223
        df_info.to_csv(output_path + '{0}'.format(file_name), mode='a', header=False, encoding='utf-8', index = False)
        pass

    except WebDriverException:
        logger.info('エラー：WebDriverException')
        #5. CSVに吐き出す。
        today = datetime.datetime.today()
        media_name = 'disruption_' + file_media_name
        file_name = '{0:%y%m%d%H%M}'.format(today)+media_name + '.csv'
        df_info.to_csv(output_path + '{0}'.format(file_name), mode='a', header=False, encoding='utf-8', index = False)
        pass


    #210408 新規にエラーを追加
    except UnexpectedAlertPresentException:
        logger.info('エラー：UnexpectedAlertPresentException')
        today = datetime.datetime.today()
        media_name = 'disruption_' + file_media_name
        file_name = '{0:%y%m%d%H%M}'.format(today)+media_name + '.csv'
        df_info.to_csv(output_path + '{0}'.format(file_name), mode='a', header=False, encoding='utf-8', index = False)

        driver.switch_to.alert.accept()
        pass


    #メモリ不足対策 500件に一度リフレッシュ 201129       
    #『InvalidSessionIdException』エラーを吐いたので、webdriverインスタンスを5件に一度都度生成してみる。220513
    #↑エラーの犯人はclose()のようなので元の500件都度に戻す。→犯人か不明だがなんかエラー吐いたので300くらいに。220701
    if num % 300 == 0:
    #都度行う、へ変更。220520
    #なんかここのcloseでエラー起きるので、一旦コメントアウトしてみる。220609
    # driver.close()
        driver.quit()
        driver = webdriver.Firefox(options=options)
    # time.sleep(5)


    #最初に一度吐き出す。
    if num == 1:
        #temporary_fileにdatetimeをつける。220222
        today = datetime.datetime.today()
        tem_file_name = '{0:%y%m%d%H%M}'.format(today)+ 'temporary_file.csv'
        df_info.to_csv(output_path +  tem_file_name, encoding='utf-8', index = False)
        #dfを初期化
        df_info = pd.DataFrame(data=None, columns = heading_columns)
    #300→100件に一度csvに追記する。220515
    elif num % 100 == 0:
        df_info.to_csv(output_path +  tem_file_name, mode='a', header=False, encoding='utf-8', index = False)
        #dfを初期化
        df_info = pd.DataFrame(data=None, columns = heading_columns)


    #4-14. 1件取得ごとに変数'num'に　+1 し、20件取得ごとに出力する。
    if num % 20 == 0:
        logger.info('\n' + '【' + str(num) + '件のデータ取得完了' + '】' + '\n')


    #2000→1000件取得ごとにお知らせメール流す処理。220515
    if num % 1000 == 0:
        now = datetime.datetime.now()
        now_time = f"{now:%Y-%m-%d %H:%M:%S}"
        subject = now_time + '【 ' + file_media_name + '_'+ str(sep_num) + ' | ' + str(num) + ' / ' + str(dic_figs) + "件 の収集が終わりました】"

        #本文はブランクでOK。211210
        body = file_media_name + '_'+ str(sep_num) + ' ' + str(num) + ' / ' + str(dic_figs) + "件 の収集が終わりました"
        

        msg = MIMEText(body, "html")
        msg["Subject"] = subject
        msg["To"] = mail_to
        msg["From"] = gmail_account

        # Gmailに接続 --- (*4)
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465,
            context=ssl.create_default_context())
        server.login(gmail_account, gmail_password)
        server.send_message(msg) # メールの送信
        # print("メール送信 complete.")
        logger.info("メール送信 complete.")


    #残り400件お知らせメール流す処理。211221
    remaining_num = 400
    if int(dic_figs) - num == remaining_num:
        now = datetime.datetime.now()
        now_time = f"{now:%Y-%m-%d %H:%M:%S}"
        subject = now_time + '【 ' + file_media_name + '_'+ str(sep_num) + ' 残り ' + str(remaining_num) + '件 です】'

        #本文はブランクでOK。211210
        body = file_media_name + '_'+ str(sep_num) + ' 残り ' + str(remaining_num) + '件 です'

        msg = MIMEText(body, "html")
        msg["Subject"] = subject
        msg["To"] = mail_to
        msg["From"] = gmail_account

        # Gmailに接続 --- (*4)
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465,
            context=ssl.create_default_context())
        server.login(gmail_account, gmail_password)
        server.send_message(msg) # メールの送信
        # print("メール送信 complete.")
        logger.info("メール送信 complete.")

    num += 1



## ここからは定型         
driver.close()
driver.quit()

#5. 一旦残りのdfをCSVに吐き出す。
df_info.to_csv(output_path + tem_file_name, mode='a', header=False, encoding='utf-8', index = False)
#5-1. ファイル名を確定し、ファイル名を変更する。
today = datetime.datetime.today()
# file_name = '{0:%y%m%d%H%M}'.format(today)+ file_media_name + '.csv'
file_name = '{0:%y%m%d%H%M}'.format(today)+ file_media_name + '_' + sep_num + '.csv'
# df_toranet.to_csv(output_path + '{0}'.format(file_name)) 
#ファイル名を変更
os.rename(output_path + tem_file_name, output_path + '{0}'.format(file_name))


#＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊
#S3自動転送用ロジックを追加。230529

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


# file_name = '/root/number_search_2_scr_220731/230510_test_s3upload.txt'

bucket = 'test-s3-220910'

logger.info('\nStart upload process to S3')

#収集ファイルの転送。230612
upload_file(output_path + file_name, bucket)
#logファイルの転送。230612
upload_file(output_path + log_file_name, bucket)
#URLファイルの転送。230612
upload_file(output_path + url_file_name, bucket)

#アップロードに60secの待機を入れる。230602
time.sleep(60)

logger.info('\nUpload to S3 is finished!!')

#＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊
#S3へ転送したファイルのアップロードチェックをし、その後EC2を停止するロジックを追加。230602

# S3クライアントを作成
s3_client = boto3.client('s3')

# バケット名とプレフィックスを指定
bucket_name = 'test-s3-220910'
prefix = ''  # オプション: ファイル名のプレフィックス

# ファイル名を格納するリスト
file_name_li = []

# バケット内のオブジェクトをリストアップ
response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

# リストアップされたオブジェクトのファイル名を取得
for obj in response['Contents']:
    file_name_li.append(obj['Key'])

# ファイル名の表示
for file_name in file_name_li:
    print(file_name)

#S3バケットに収集したファイル名が存在している場合、片付けをしEC2を停止する。230602
if file_name in file_name_li:

    #7. 片付け
    # print(media_name + '完了')
    logger.info(media_name + '完了')


    t4 = time.time()
    ela_time = t4-t3
    logger.info(f"収集時間：{elapsed_time}")

    elapsed_time_2 = t4-t1
    logger.info(f"全体時間：{elapsed_time_2}")

    complete_media_name = 'complete' + media_name
    # print('\n' + '【' + complete_media_name + '】' + '\n')
    logger.info('\n' + '【' + complete_media_name + '】' + '\n')


    #6-2, 完了のメール送信。211024
    #もしlogger内容でメール送信できなければ、↓に変更する。
    now = datetime.datetime.now()
    now_time = f"{now:%Y-%m-%d %H:%M:%S}"
    # subject = now_time + '【' + media_name  + "】の収集が完了しました。"
    subject = now_time + '【（S3アップロード完了）' + file_media_name + '_' + sep_num + ' | ' + str(num) +  "件】の収集が完了しました。EC2を停止します。"


    #経過時間を『分』に修正して表示
    era_min = ela_time // 60
    body = '収集時間は ' + str(era_min) + ' 分。\n【収集案件数は、' + str(num) + '件でした。】\n'


    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["To"] = mail_to
    msg["From"] = gmail_account

    # Gmailに接続 --- (*4)
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465,
        context=ssl.create_default_context())
    server.login(gmail_account, gmail_password)
    server.send_message(msg) # メールの送信
    # print("メール送信 complete.")
    logger.info("メール送信 complete.")

    #ハンドラーを削除。
    logger.removeHandler(s_handler)
    logger.removeHandler(f_handler)


    #ディレクトリ内のファイルを全削除する。230611
    #import os
    logger.info('ディレクトリ内のファイルを全削除します。')
    def delete_files_in_directory(directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Deleted file: {file_path}")

    # ディレクトリのパスを指定
    directory_path = output_path_ec2

    # ディレクトリ内のファイルを削除
    delete_files_in_directory(directory_path)

    logger.info('\nディレクトリ内のファイルを全削除しました。')

    ### EC2を停止する。230611
    #インスタンスIDを取得。上部へ移動。230608
    #instance_id = 'i-0094acb312783fe81'
    #instance_id = '個別入力①'

    #EC2クライアントを作成
    ec2_client = boto3.client('ec2', region_name='ap-northeast-1')

    #EC2インスタンスを停止
    response = ec2_client.stop_instances(InstanceIds=[instance_id])

#停止リクエストが成功したかどうかを確認
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        logger.info('EC2インスタンスの停止リクエストが送信されました。')
    #ハンドラーを削除。
        logger.removeHandler(s_handler)
        logger.removeHandler(f_handler)
    else:
        logger.info('EC2インスタンスの停止リクエストに失敗しました。')

#S3へのファイルアップロードが失敗している場合の処理。230608
else:

    #6-2, 完了のメール送信。211024
    #もしlogger内容でメール送信できなければ、↓に変更する。
    now = datetime.datetime.now()
    now_time = f"{now:%Y-%m-%d %H:%M:%S}"
    # subject = now_time + '【' + media_name  + "】の収集が完了しました。"
    subject = now_time + ' ' + file_media_name + ' のS3アップロードが失敗しております!!!!EC2に接続し、ログをチェックしてください。'

    #経過時間を『分』に修正して表示
    era_min = ela_time // 60
    body = '収集時間は ' + str(era_min) + ' 分。\n【収集案件数は、' + str(num) + '件でした。】\n'


    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["To"] = mail_to
    msg["From"] = gmail_account

    # Gmailに接続 --- (*4)
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465,
        context=ssl.create_default_context())
    server.login(gmail_account, gmail_password)
    server.send_message(msg) # メールの送信
    # print("メール送信 complete.")
    logger.info("メール送信 complete.")

    #ハンドラーを削除。
    logger.removeHandler(s_handler)
    logger.removeHandler(f_handler)


# #Excelファイルも吐き出すため、吐き出したCSVファイルを読み込む。
# df_re = pd.read_csv(output_path + file_name, low_memory=False , dtype={'求人ID': object, '企業ID': object, '電話番号ハイフンなし': object}, encoding='utf-8')


# #3-2. 新着dfをハイパーリンクを削除し（options={'strings_to_urls':False}）xlsxで吐き出す。
# # file_name_new = '{0:%y%m%d%H%M}'.format(today)+ file_media_name + '.xlsx'
# file_name_new = '{0:%y%m%d%H%M}'.format(today)+ file_media_name + '_' + sep_num + '.xlsx'
# writer = pd.ExcelWriter(output_path + file_name_new, options={'strings_to_urls':False})
# df_re.to_excel(writer, index=False)
# writer.close()

# ## 3-3. フォントをExcelのデフォルトに変更する。210531
# sheet_name = 'Sheet1'
# inputfile = output_path + file_name_new


# # read input xlsx
# wb1 = openpyxl.load_workbook(filename=inputfile)
# # シートを取得 
# ws1 = wb1[sheet_name]

# # set font
# font = Font(name='游ゴシック Regular (本文)', size=12)

# # write in sheet
# # セル番地を取得
# for cells in tuple(ws1.rows):
#     for cell in cells:
#         ws1[cell.coordinate].font = font

# # # save xlsx file
# wb1.save(inputfile)


# #7. 片付け
# # print(media_name + '完了')
# logger.info(media_name + '完了')

# #bash判定のダミーファイルを作成する。211208
# test_file = pathlib.Path(judge_file_path + 'judge.txt')
# test_file.touch()


# t4 = time.time()
# ela_time = t4-t1

# logger.info(f"全体時間：{ela_time}")

# complete_media_name = 'complete' + file_media_name
# # print('\n' + '【' + complete_media_name + '】' + '\n')
# logger.info('\n' + '【' + complete_media_name + '】' + '\n')


# #6-2, 完了のメール送信。211024

# #もしlogger内容でメール送信できなければ、↓に変更する。
# now = datetime.datetime.now()
# now_time = f"{now:%Y-%m-%d %H:%M:%S}"
# subject = now_time + '【' + file_media_name + '_'+ str(sep_num) + "】の収集が完了しました。"

# #経過時間を『分』に修正して表示
# era_min = ela_time // 60
# body = '収集時間は ' + str(era_min) + ' 分。\n【収集案件数は、' + str(num) + '件でした。】\n'


# msg = MIMEText(body, "html")
# msg["Subject"] = subject
# msg["To"] = mail_to
# msg["From"] = gmail_account

# # Gmailに接続 --- (*4)
# server = smtplib.SMTP_SSL("smtp.gmail.com", 465,
#     context=ssl.create_default_context())
# server.login(gmail_account, gmail_password)
# server.send_message(msg) # メールの送信
# # print("メール送信 complete.")
# logger.info("メール送信 complete.")

# #ハンドラーを削除。
# logger.removeHandler(s_handler)
# logger.removeHandler(f_handler)


# # prof = LineProfiler()
# # prof.add_function(scrape)
# # prof.runcall(scrape)
# # prof.print_stats()


