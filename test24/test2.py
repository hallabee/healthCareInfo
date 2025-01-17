from flask import Flask, render_template, request, redirect, Response
from flask_mysqldb import MySQL
from datetime import datetime
import cv2
import mediapipe as mp
import numpy as np
from PIL import Image
import io

app = Flask(__name__)

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "user"
app.config['MYSQL_PASSWORD'] = "password"
app.config['MYSQL_DB'] = "database"

mysql = MySQL(app)

# 로그인 및 회원가입 버튼 페이지 - 초기화면 페이지
@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("select * from user where user_id = %s and password = %s", (user_id, password))
        user = cur.fetchone()
        cur.close()

        if user:
            return redirect('/login')
        else:
            error_message = '아이디 또는 비밀번호를 잘못 입력했습니다. 다시 확인해주세요.'
            return render_template('index2.html', error_message=error_message)

    return render_template('index2.html')

# 회원가입 페이지
@app.route('/register2', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        user_id = request.form['user_id']
        password = request.form['password']
        phone = request.form['phone']
        address = request.form['address']

        cur = mysql.connection.cursor()
        cur.execute("insert into user (username, user_id, password, phone, address) values (%s,%s,%s,%s,%s)", (username, user_id, password, phone, address))
        mysql.connection.commit()
        cur.close()

        return redirect('/')
    return render_template('register2.html')

# 로그인했을때 뜨는 메인 페이지
@app.route('/login', methods=['GET', 'POST'])
def login():
    cur = mysql.connection.cursor()
    cur.execute("select oldname from oldperson")
    oldnames = [row[0] for row in cur.fetchall()]
    cur.close()

    return render_template('login.html', oldnames=oldnames)


# 어르신 추가 페이지
@app.route('/oldperson', methods=['GET','POST'])

def oldperson():
    if request.method == 'POST':
        oldname = request.form['oldname']
        sex = request.form['sex']
        birth = request.form['birth']
        birth = datetime.strptime(birth, '%Y-%m-%d').date()
        age = request.form['age']
        height = request.form['height']
        weight = request.form['weight']
        guardian = request.form['guardian']
        phone = request.form['phone']
        address = request.form['address']
        road_name_address=request.form['road_name_address']
        detailed_address=request.form['detailed_address']

        cur = mysql.connection.cursor()
        cur.execute(
            "insert into oldperson (oldname, sex, birth, age, height, weight, guardian, phone, address, road_name_address, detailed_address) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (oldname, sex, birth, int(age), float(height), float(weight), guardian, phone, address, road_name_address, detailed_address))
        mysql.connection.commit()
        cur.close()

        return redirect('login')

    cur = mysql.connection.cursor()
    cur.execute("select oldname from oldperson")
    oldnames = [row[0] for row in cur.fetchall()]
    cur.close()

    return render_template('oldperson.html', oldnames=oldnames)

#어르신 상세 정보 페이지
@app.route('/oldperson_info/<oldname>', methods=['GET'])
def oldperson_info(oldname):
    cur = mysql.connection.cursor()

    cur.execute("select oldname from oldperson")
    oldnames = [row[0] for row in cur.fetchall()]

    cur.execute("select * from oldperson where oldname = %s", [oldname])
    oldperson_info = cur.fetchone()

    cur.execute("select * from healthinfo where oldname = %s ORDER BY date DESC limit 5", [oldname])
    healthinfo = cur.fetchall()

    cur.execute("select * from healthcare where oldname = %s ORDER BY date DESC limit 5", [oldname])
    healthcare = cur.fetchall()

    cur.close()
    return render_template('oldperson_info.html',oldnames=oldnames, oldperson_info=oldperson_info, healthinfo=healthinfo, healthcare=healthcare)

# 건강 정보 상세 페이지
@app.route('/oldperson_all_info/<oldname>', methods=['GET','POST'])
def oldperson_all_info(oldname):
    cur = mysql.connection.cursor()

    cur.execute("select oldname from oldperson")
    oldnames = [row[0] for row in cur.fetchall()]

    cur.execute("select * from oldperson where oldname = %s", [oldname])
    oldperson_info = cur.fetchone()

    cur.execute("select * from healthinfo where oldname = %s ORDER BY date DESC", [oldname])
    healthinfo = cur.fetchall()

    cur.close()
    return render_template('oldperson_all_info.html', oldnames=oldnames, oldperson_info=oldperson_info,healthinfo=healthinfo)

# 건강 운동 상세 페이지
@app.route('/oldperson_all_care/<oldname>', methods=['GET','POST'])
def oldperson_all_care(oldname):
    cur = mysql.connection.cursor()

    cur.execute("select oldname from oldperson")
    oldnames = [row[0] for row in cur.fetchall()]

    cur.execute("select * from oldperson where oldname = %s", [oldname])
    oldperson_info = cur.fetchone()

    cur.execute("select * from healthcare where oldname = %s ORDER BY date DESC limit 5", [oldname])
    healthcare = cur.fetchall()

    cur.close()
    return render_template('oldperson_all_care.html', oldnames=oldnames, oldperson_info=oldperson_info,healthcare=healthcare)

# 건강 정보 입력 기능
@app.route('/oldperson_info/<oldname>', methods=['POST'])
def healthinfo(oldname):
    date = request.form['date']
    blood_pressure = request.form['blood_pressure']
    blood_sugar = request.form['blood_sugar']
    healthinfo = request.form['healthinfo']

    cur = mysql.connection.cursor()
    cur.execute("insert into healthinfo (oldname, date, blood_pressure, blood_sugar, healthinfo) VALUES (%s, %s, %s, %s, %s)",
                (oldname, date, blood_pressure, blood_sugar, healthinfo))
    mysql.connection.commit()
    cur.close()

    return redirect('/oldperson_info/' + oldname)

# 어르신 정보 삭제하기
@app.route('/delete_oldperson/<oldname>', methods=['POST'])
def delete_oldperson(oldname):
    cur = mysql.connection.cursor()
    cur.execute("delete from oldperson where oldname = %s", [oldname])
    mysql.connection.commit()
    cur.close()
    return redirect('/login')

# 건강 정보 삭제하기
@app.route('/delete_healthinfo/<oldname>/<id>', methods=['POST'])
def delete_healthinfo(oldname, id):
    cur = mysql.connection.cursor()
    cur.execute("delete from healthinfo where id = %s", [id])
    mysql.connection.commit()
    cur.close()
    return redirect('/oldperson_all_info/' + oldname)

# 운동 정보 삭제하기
@app.route('/delete_healthcare/<oldname>/<id>', methods=['POST'])
def delete_healthcare(oldname, id):
    cur = mysql.connection.cursor()
    cur.execute("delete from healthcare where id = %s", [id])
    mysql.connection.commit()
    cur.close()
    return redirect('/oldperson_all_care/' + oldname)

# 운동 선택
@app.route('/health_choice/<oldname>', methods=['GET', 'POST'])
def health_choice(oldname):
    cur = mysql.connection.cursor()

    cur.execute("select oldname from oldperson")
    oldnames = [row[0] for row in cur.fetchall()]

    cur.execute("select * from oldperson where oldname = %s", [oldname])
    oldperson_info = cur.fetchone()

    cur.execute("select * from healthinfo where oldname = %s ORDER BY date DESC limit 5", [oldname])
    healthinfo = cur.fetchall()

    cur.close()

    return render_template('health_choice.html', oldnames=oldnames, oldperson_info=oldperson_info,
                           healthinfo=healthinfo)

#------------------------------------------------------------------------------------------------------

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)  # 웹캠으로부터 비디오 캡처

# 사용자 지정 연결 정의
user_connections = [
    (0, 10), # 코와 오른쪽 입술
    (0, 9), # 코와 왼쪽 입술
    (9, 10), # 입술
    (11, 12), # 어깨
    (11, 13), # 왼쪽 어깨와 왼쪽 팔꿈치
    (13, 15), # 왼쪽 팔꿈치와 왼쪽 손목
    (12, 14), # 오른쪽 어깨와 오른쪽 팔꿈치
    (14, 16) # 오른쪽 팔꿈치와 오른쪽 손목
]

def calculate_angle(a, b, c):
    a = np.array(a)  # 시작점
    b = np.array(b)  # 중심
    c = np.array(c)  # 끝점

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0]) #라디안값 계산
    angle = np.abs(radians * 180.0 / np.pi) #라디안 값에서 각도로 변환

    if angle > 180.0: #값이 180도 이상이면 360에서 angle값을 뺀다
        angle = 360 - angle

    return angle

target_count = 0  # 목표 카운트
counter = 0
stage = None
current_level = 1
target_exercise = 'arm'

def generate():
    global target_count, counter, stage, target_exercise
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        if target_exercise == 'arm' :
            angle_up = 155
            angle_down = 60
            if current_level == 1:
                angle_up = 155
                angle_down = 60
            elif current_level == 2:
                angle_up = 165
                angle_down = 50
            elif current_level == 3:
                angle_up = 175
                angle_down = 40
        elif target_exercise =='shoulder':
            angle_up = 130
            angle_down = 40
            if current_level == 1:
                angle_up = 130
                angle_down = 40
            elif current_level == 2:
                angle_up = 140
                angle_down = 30
            elif current_level == 3:
                angle_up = 150
                angle_down = 20

        if counter >= target_count and target_count != 0:
            counter = 0
            target_count = 0
            # PNG 파일 불러오기
            image = cv2.imread('static\success.png')

            # 필요한 경우 이미지 크기 조정
            image = cv2.resize(image, (640, 480))

            # PIL 이미지로 변환
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

            # PIL 이미지를 바이트로 변환
            byte_arr = io.BytesIO()
            pil_image.save(byte_arr, format='JPEG')

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + byte_arr.getvalue() + b'\r\n')

            break

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        results = pose.process(image)

        image.flags.writeable = True

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            if target_exercise == 'arm':
                l_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                l_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                l_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                angle = calculate_angle(l_shoulder, l_elbow, l_wrist)
                text_pos = (int(l_elbow[0] * image.shape[1]), int(l_elbow[1] * image.shape[0]))

            elif target_exercise == 'shoulder':
                l_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                              landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                l_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                l_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                              landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]

                angle = calculate_angle(l_elbow, l_shoulder,l_hip)
                text_pos = (int(l_shoulder[0] * image.shape[1]), int(l_shoulder[1] * image.shape[0]))

            # 각도에 따른 카운트
            if angle > angle_up:
                stage = "down"
            if angle < angle_down and stage == 'down':
                stage = "up"
                counter += 1
                print(counter)

            # 사용자 지정 연결로 랜드마크 선 그리기
            mp_drawing.draw_landmarks(image, results.pose_landmarks, user_connections,landmark_drawing_spec=None)

        if angle <= angle_down or angle >= angle_up:
            color = (0, 255, 0)
        else:
            color = (255, 0, 0)

        cv2.putText(image, str(int(angle)),text_pos,
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
        # 카운트 표시
        cv2.putText(image, 'Count: ' + str(counter),
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255),2)

        # PIL 이미지로 변환
        pil_image = Image.fromarray(image)

        # PIL 이미지를 바이트로 변환
        byte_arr = io.BytesIO()
        pil_image.save(byte_arr, format='JPEG')

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + byte_arr.getvalue() + b'\r\n')

#웹캠 시작
@app.route('/start_webcam', methods=['POST'])
def start_webcam():
    global cap, counter
    counter = 0
    cap = cv2.VideoCapture(0)
    return '웹캠 시작'

#웹캠 종료
@app.route('/stop_webcam', methods=['POST'])
def stop_webcam():
    global cap
    cap.release()
    return '웹캠 종료'

#운동 정보 입력
@app.route('/transmission', methods=['POST'])
def transmission():
    oldname = request.form['oldname']
    count = request.form['count']
    level = request.form['level']
    date = datetime.now().strftime('%Y-%m-%d')
    exercise = request.form['filename']
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO healthcare (oldname, date, exercise, count, level) VALUES (%s, %s, %s, %s, %s)',
                (oldname, date, exercise, int(count), int(level)))
    mysql.connection.commit()
    cur.close()
    return oldperson_info(oldname)

#웸캠
@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

#팔 운동 페이지
@app.route('/healthcare/<oldname>', methods=['POST'])
def healthcare(oldname):
    global target_exercise
    target_exercise = 'arm'
    cur = mysql.connection.cursor()

    cur.execute("select oldname from oldperson")
    oldnames = [row[0] for row in cur.fetchall()]

    cur.execute("select * from oldperson where oldname = %s", [oldname])
    oldperson_info = cur.fetchone()

    cur.execute("select * from healthinfo where oldname = %s ORDER BY date DESC limit 5", [oldname])
    healthinfo = cur.fetchall()

    cur.close()
    return render_template('healthcare.html', oldnames=oldnames, oldperson_info=oldperson_info,
                           healthinfo=healthinfo)

#어깨 운동 페이지
@app.route('/healthcare_shoulder/<oldname>', methods=['POST'])
def healthcare_shoulder(oldname):
    global target_exercise
    target_exercise = 'shoulder'
    cur = mysql.connection.cursor()

    cur.execute("select oldname from oldperson")
    oldnames = [row[0] for row in cur.fetchall()]

    cur.execute("select * from oldperson where oldname = %s", [oldname])
    oldperson_info = cur.fetchone()

    cur.execute("select * from healthinfo where oldname = %s ORDER BY date DESC limit 5", [oldname])
    healthinfo = cur.fetchall()

    cur.close()
    return render_template('healthcare_shoulder.html', oldnames=oldnames, oldperson_info=oldperson_info,
                           healthinfo=healthinfo)

#healthcare 카운트 입력
@app.route('/set_count', methods=['POST','GET'])
def set_count():
    global target_count, counter, stage, current_level,target_exercise
    target_count = int(request.form['count'])
    counter = 0  # 카운터 초기화
    stage = None  # 스테이지 초기화

    current_level = int(request.form['level'])

    oldname = request.form['oldname']
    if target_exercise == 'arm' :
        return healthcare(oldname)
    elif target_exercise == 'shoulder' :
        return healthcare_shoulder(oldname)


#시니어 팔운동
@app.route('/exercise_arm', methods=['POST','GET'])
def exercise_arm():
    global counter, target_exercise
    target_exercise = 'arm'
    counter = 0
    return render_template('exercise_arm.html')

#시니어 어깨운동
@app.route('/exercise_shoulder', methods=['POST','GET'])
def exercise_shoulder():
    global counter, target_exercise
    target_exercise = 'shoulder'
    counter = 0
    return render_template('exercise_shoulder.html')

#시니어 exercise 카운트 입력
@app.route('/set_count_test', methods=['POST'])
def set_count_test():
    global target_count, counter, stage, current_level, target_exercise
    target_count = int(request.form['count'])
    counter = 0  # 카운터 초기화
    stage = None  # 스테이지 초기화

    current_level = int(request.form['level'])

    if target_exercise == 'arm' :
        return exercise_arm()
    elif target_exercise == 'shoulder' :
        return exercise_shoulder()

def main():
    app.run(host='127.0.0.1', debug=True, port=80)
if __name__ == "__main__":
    main();