# Nhóm 6

<h1>Lexical Analyzer</h1>

<h2>Cách chạy module</h2>

1. Tải và cài đặt Python bản 3.11 trở lên https://www.python.org/downloads/.
2. Mở cửa sổ dòng lệnh tại thư mục chính.
3. Ném file code .vc cần phân tích từ vựng vào folder input để dùng tên file cho bước 4 (nếu không thì dùng đường dẫn absolute).
4. Chạy module lexer: `python -m lexer file_url_1 [file_url_2...]`
5. Xem kết quả tại folder output (đuôi .vctok)
   > VD: `python -m lexer sample.vc example_fib.vc example_gcd.vc`<br><br>
   > Để xem trợ giúp và các option khác: `python -m lexer -h`
   > ```console
   > usage: python -m lexer [-h] [-l LEX] [-w] input_urls [input_urls ...]
   >
   > Bộ phân tích từ vựng.
   >
   >positional arguments:
   >input_urls         Tên (nếu đặt trong folder input) hoặc đường dẫn absolute của file đầu vào
   >
   >options:
   >-h, --help         show this help message and exit
   >-l LEX, --lex LEX  Tên file automaton data cho lexical analyzer (.dat, mặc định lex.dat)
   >-w, --whole        Đọc toàn bộ file input thay vì từng dòng (đối với file nhỏ)
   >```

<h2>Cấu trúc source code</h2>

<ul>
<li>input: chứa các file code đầu vào (*.vc)</li>
<li>output:  chứa các file đầu ra tương ứng (*.vc.tok)</li>
<li>lexer: module lexer, bao gồm:</li>
<ul>
   <li>main.py: Chứa hàm main() và lex_analyze() được gọi khi module chạy, cung cấp giao diện CLI.</li>
   <li>lexer_builder.py: Chứa LexerBuilder và các hàm dùng để phân tích từng dòng trong file .dat để từ đó xây dựng lexer.</li>
   <li>lexer.py: Định nghĩa Lexer, hàm is_newline() hỗ trợ xuống dòng.</li>
   state.py: Định nghĩa các lớp trạng thái.
   <li>state_attributes.py: Định nghĩa các lớp thuộc tính của state (Escape, Token).</li>
   <li>lexer_result.py: Định nghĩa đầu ra của lexer (LexicalResult, LexicalError, Location, Position).</li>
   <li>lex.dat: Khai báo thông tin dùng để xây dựng lexer cho ngôn ngữ VC. Format và cách thức sử dụng được comment và mô tả ngay trong file.</li>
</ul>
<li>README.md: Cách chạy code và một số thông tin cơ bản.</li>
</ul>
