from flask import Flask, render_template, request, url_for, redirect
from datetime import datetime
from models import db, CHD
from config import Config
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app)
db.init_app(app)

with app.app_context():
    db.create_all()
    

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@socketio.on('user_message')
def handle_user_message(msg):
    print('User message: ' + msg)
    emit('new_question', msg, broadcast=True)

@socketio.on('admin_response')
def handle_admin_response(response):
    print('Admin response: ' + response)
    emit('response', response, broadcast=True)


@app.route("/")
def chuyenHuong():
    return redirect(url_for('xemTuVi'))

@app.route("/TuVi", methods=["GET", "POST"])
def xemTuVi():
    name = age = zodiac_sign = chinese_zodiac_sign = None
    error = None
    if request.method == "POST":
        name = request.form.get('name')
        
        birth_day = request.form.get('day')
        birth_month = request.form.get('month')
        birth_year = request.form.get('year')

        if birth_day and birth_month and birth_year:
            try:
                birth_day = int(birth_day)
                birth_month = int(birth_month)
                birth_year = int(birth_year)

                if not (1 <= birth_day <= 31 and 1 <= birth_month <= 12 and 1900 <= birth_year <= datetime.now().year):
                    error = "Ngày tháng năm sinh không hợp lệ."
                else:
                    current_year = datetime.now().year
                    age = current_year - birth_year

                    zodiac_signs = [
                        ('Ma Kết', (1, 19)), ('Bảo Bình', (2, 18)), ('Song Ngư', (3, 20)),
                        ('Bạch Dương', (4, 19)), ('Kim Ngưu', (5, 20)), ('Song Tử', (6, 20)),
                        ('Cự Giải', (7, 22)), ('Sư Tử', (8, 22)), ('Xử Nữ', (9, 22)),
                        ('Thiên Bình', (10, 22)), ('Bọ Cạp', (11, 21)), ('Nhân Mã', (12, 21)), ('Ma Kết', (12, 31))
                    ]
                    
                    birth_date = (birth_month, birth_day)
                    zodiac_sign = next(
                        (sign for sign, (end_month, end_day) in zodiac_signs
                         if birth_date <= (end_month, end_day)),
                        'Ma Kết'
                    )

                    chinese_zodiac = [
                        'Thân', 'Dậu', 'Tuất', 'Hợi', 'Tý', 'Sửu', 
                        'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi'
                    ]
                    chinese_zodiac_sign = chinese_zodiac[birth_year % 12]
            except ValueError:
                error = "Ngày tháng năm sinh không hợp lệ."

        else:
            error = "Vui lòng điền đầy đủ thông tin ngày tháng năm sinh."

    return render_template('nhapThongtin.html', name=name, age=age, zodiac_sign=zodiac_sign, chinese_zodiac_sign=chinese_zodiac_sign, error=error)

@app.route("/CHD", methods=["GET", "POST"])
def ThongTinCHD():
    zodiac = None
    error = None
    if request.method == "POST":
        ZodiacImage = request.form['searchInput']
        zodiac = CHD.query.filter_by(TenCHD=ZodiacImage).first()

        if zodiac:
            return render_template('CHD.html', ZodiacImage=ZodiacImage, zodiac=zodiac)
        else:
            error = "Không tìm thấy cung hoàng đạo"

    return render_template('CHD.html', ZodiacImage=None, zodiac=zodiac, error=error)


@app.route("/tuoi_hop", methods=["GET", "POST"])
def tuoi_hop():
    zodiac_compatibility = []
    error = None

    if request.method == "POST":
        birth_year = request.form.get('birth_year')
        gender = request.form.get('gender')
        
        try:
            birth_year = int(birth_year)
            zodiac_signs = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tị", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
            zodiac = zodiac_signs[(birth_year - 4) % 12]

            tam_hop = {
                "Hợi": {"nam": ["Mão", "Mùi"], "nu": ["Mão", "Mùi"]},
                "Mão": {"nam": ["Hợi", "Mùi"], "nu": ["Hợi", "Mùi"]},
                "Mùi": {"nam": ["Hợi", "Mão"], "nu": ["Hợi", "Mão"]},
                "Thân": {"nam": ["Tý", "Thìn"], "nu": ["Tý", "Thìn"]},
                "Tý": {"nam": ["Thân", "Thìn"], "nu": ["Thân", "Thìn"]},
                "Thìn": {"nam": ["Thân", "Tý"], "nu": ["Thân", "Tý"]},
                "Tị": {"nam": ["Dậu", "Sửu"], "nu": ["Dậu", "Sửu"]},
                "Dậu": {"nam": ["Tị", "Sửu"], "nu": ["Tị", "Sửu"]},
                "Sửu": {"nam": ["Tị", "Dậu"], "nu": ["Tị", "Dậu"]},
                "Dần": {"nam": ["Ngọ", "Tuất"], "nu": ["Ngọ", "Tuất"]},
                "Ngọ": {"nam": ["Dần", "Tuất"], "nu": ["Dần", "Tuất"]},
                "Tuất": {"nam": ["Dần", "Ngọ"], "nu": ["Dần", "Ngọ"]},
            }

            tuoi_khong_hop = {
                "Hợi": ["Thân", "Dậu"],
                "Mão": ["Thân", "Dậu"],
                "Mùi": ["Thân", "Dậu"],
                "Thân": ["Hợi", "Mùi"],
                "Tý": ["Mùi", "Hợi"],
                "Thìn": ["Mùi", "Hợi"],
                "Tị": ["Dần", "Tuất"],
                "Dậu": ["Dần", "Tuất"],
                "Sửu": ["Dần", "Tuất"],
                "Dần": ["Tị", "Dậu"],
                "Ngọ": ["Tị", "Dậu"],
                "Tuất": ["Tị", "Dậu"],
            }

            compatibility_scores = {z: 5 for z in zodiac_signs}

            if gender == 'male':
                for compatible in tam_hop.get(zodiac, {}).get("nam", []):
                    compatibility_scores[compatible] = 10
            elif gender == 'female':
                for compatible in tam_hop.get(zodiac, {}).get("nu", []):
                    compatibility_scores[compatible] = 10

            for khong_hop in tuoi_khong_hop.get(zodiac, []):
                compatibility_scores[khong_hop] = 0

            sorted_scores = sorted(compatibility_scores.items(), key=lambda x: x[1], reverse=True)
            zodiac_compatibility = sorted_scores
            
        except ValueError:
            error = "Năm sinh không hợp lệ."

    return render_template('tuoiHop.html', zodiac_compatibility=zodiac_compatibility, error=error)



@app.route("/cung_hoang_dao", methods=["GET", "POST"])
def cung_hoang_dao():
    zodiac_compatibility = []
    error = None

    if request.method == "POST":
        try:
            zodiac_sign = request.form.get('zodiac_sign')
            gender = request.form.get('gender')

            compatibility = {
                'Nam': {
                    'Bạch Dương': ['Sư Tử', 'Nhân Mã'],
                    'Sư Tử': ['Bạch Dương', 'Nhân Mã'],
                    'Nhân Mã': ['Bạch Dương', 'Sư Tử'],
                    'Kim Ngưu': ['Ma Kết', 'Xử Nữ'],
                    'Song Tử': ['Thiên Bình', 'Bảo Bình'],
                    'Thiên Bình': ['Song Tử', 'Bảo Bình'],
                    'Bảo Bình': ['Song Tử', 'Thiên Bình'],
                    'Xử Nữ': ['Kim Ngưu', 'Ma Kết'],
                    'Ma Kết': ['Kim Ngưu', 'Xử Nữ'],
                    'Cự Giải': ['Bọ Cạp', 'Song Ngư'],
                    'Bọ Cạp': ['Cự Giải', 'Song Ngư'],
                    'Song Ngư': ['Cự Giải', 'Bọ Cạp'],
                },
                'Nữ': {
                    'Bạch Dương': ['Nhân Mã', 'Sư Tử'],
                    'Sư Tử': ['Nhân Mã', 'Bạch Dương'],
                    'Nhân Mã': ['Bạch Dương', 'Sư Tử'],
                    'Kim Ngưu': ['Ma Kết', 'Xử Nữ'],
                    'Song Tử': ['Thiên Bình', 'Bảo Bình'],
                    'Thiên Bình': ['Song Tử', 'Bảo Bình'],
                    'Bảo Bình': ['Song Tử', 'Thiên Bình'],
                    'Xử Nữ': ['Ma Kết', 'Kim Ngưu'],
                    'Ma Kết': ['Kim Ngưu', 'Xử Nữ'],
                    'Cự Giải': ['Bọ Cạp', 'Song Ngư'],
                    'Bọ Cạp': ['Cự Giải', 'Song Ngư'],
                    'Song Ngư': ['Cự Giải', 'Bọ Cạp'],
                }
            }

            if zodiac_sign in compatibility[gender]:
                zodiac_compatibility = compatibility[gender][zodiac_sign]
            else:
                error = "Cung hoàng đạo không hợp lệ."

        except Exception as e:
            error = str(e)

    return render_template('cunghoangdao.html', zodiac_compatibility=zodiac_compatibility, error=error)

@app.route("/thiencan_diachi", methods=["GET", "POST"])
def thiencan_diachi():
    can = None
    chi = None
    error = None

    if request.method == "POST":
        birth_year = request.form.get('birth_year')

        try:
            birth_year = int(birth_year)
            can = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"][(birth_year - 4) % 10]
            chi = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tị", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"][(birth_year - 4) % 12]
        except ValueError:
            error = "Năm sinh không hợp lệ."

    return render_template('thiencan_diachi.html', can=can, chi=chi, error=error)

@app.route("/ThongTin")
def ThongTin():
    return render_template('ThongTin.html')

@app.route("/ngay_tot", methods=["GET", "POST"])
def xem_ngay_tot():
    ngay_tot = None
    error = None

    if request.method == "POST":
        try:
            ngay = int(request.form.get('day'))
            thang = int(request.form.get('month'))
            nam = int(request.form.get('year'))

            if not (1 <= ngay <= 31 and 1 <= thang <= 12 and 1900 <= nam <= datetime.now().year):
                error = "Ngày tháng năm không hợp lệ."
            else:
                # Quy tắc để tính toán ngày tốt dựa vào ngày, tháng, năm
                if ngay % 3 == 0:
                    ngay_tot = "Ngày này tốt cho việc khởi hành, đi xa."
                elif ngay % 5 == 0:
                    ngay_tot = "Ngày này tốt cho việc kết hôn, cưới hỏi."
                elif ngay % 7 == 0:
                    ngay_tot = "Ngày này tốt cho việc mua nhà, xây dựng."
                elif ngay % 2 == 0:
                    ngay_tot = "Ngày này tốt cho việc làm ăn, kinh doanh."
                else:
                    ngay_tot = "Ngày này tốt cho việc học hành và thi cử."
        except ValueError:
            error = "Vui lòng nhập ngày tháng năm hợp lệ."

    return render_template('ngay_tot.html', ngay_tot=ngay_tot, error=error)

@app.route("/ngay_xau", methods=["GET", "POST"])
def ngay_xau():
    bad_day_advice = ""
    error = None

    if request.method == "POST":
        try:
            birth_year = request.form.get('birth_year')
            birth_month = request.form.get('birth_month')
            birth_day = request.form.get('birth_day')

            birth_date = datetime(int(birth_year), int(birth_month), int(birth_day))

            weekdays_mapping = {
                "Sunday": "Chủ Nhật",
                "Monday": "Thứ Hai",
                "Tuesday": "Thứ Ba",
                "Wednesday": "Thứ Tư",
                "Thursday": "Thứ Năm",
                "Friday": "Thứ Sáu",
                "Saturday": "Thứ Bảy"
            }

            bad_days = {
                "Chủ Nhật": "Không nên khởi hành, ký kết hợp đồng.",
                "Thứ Hai": "Không nên bắt đầu công việc mới.",
                "Thứ Ba": "Không nên xây sửa nhà cửa.",
                "Thứ Tư": "Không nên cưới hỏi, đầu tư.",
                "Thứ Năm": "Không nên ra quyết định lớn.",
                "Thứ Sáu": "Không nên thực hiện các giao dịch tài chính.",
                "Thứ Bảy": "Không nên tham gia tranh cãi, kiện tụng.",
            }

            weekday_english = birth_date.strftime("%A")
            weekday_vietnamese = weekdays_mapping.get(weekday_english, "")
            bad_day_advice = bad_days.get(weekday_vietnamese, "Ngày này không có lưu ý đặc biệt.")

        except ValueError:
            error = "Ngày tháng năm sinh không hợp lệ."

    return render_template('ngay_xau.html', bad_day_advice=bad_day_advice, error=error)




if __name__ == "__main__":
    socketio.run(app, debug=True)
