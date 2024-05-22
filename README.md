# Nhóm 6

<h1>Syntax Parser</h2>

<h2>Cách chạy module Parser</h2>

1. Tải và cài đặt Python bản 3.12 trở lên https://www.python.org/downloads/.
2. Mở cửa sổ dòng lệnh tại thư mục chính của source code.
3. Ném file code .vc cần phân tích cú pháp vào folder input để dùng tên file cho bước 4 (nếu không thì dùng đường dẫn absolute).
4. Chạy module parser: `python -m parser file_url_1 [file_url_2...]`
5. Thêm các flag thích hợp. Ví dụ để build từ table và in ra dưới dạng verbose (JSON) với indent là 2:
   > python -m parser -t -v -i=2 sample.vc   
6. Xem kết quả tại folder output (đuôi .vcps), có thể click vào link url trên command line.
   > - VD: python -m parser sample.vc dangling_else.vc left_assoc.vc right_assoc.vc 
   > - Để xem trợ giúp và các option khác: `python -m parser -h`
   > ```
   >usage: python -m parser [-h] [-t] [-i INDENT] [-v] [-r {0,1,2}] [-m] [-e] [-a] [-w] input_files [input_files ...]
   >
   >Bộ phân tích cú pháp.
   >
   >positional arguments:
   >input_files           Tên (nếu đặt trong folder input) hoặc đường dẫn absolute của file đầu vào
   >
   >options:
   >-h, --help            show this help message and exit
   >-t, --table           Build parser trực tiếp từ table.dat.
   >-i INDENT, --indent INDENT
   >                        Indent size cho verbose và normal brackets. Mặc định 4.
   >-v, --verbose         In ra cây AST theo định dạng JSON.
   >-r {0,1,2}, --reduce_level {0,1,2}
   >                        Cấp độ loại bỏ các cặp dấu ngoặc thừa. 0 - Không bỏ; 1 - Giữ lại các cặp chỉ chứa duy nhất
   >                        leaf_value; 2 - Loại các cặp chỉ chứa duy nhất leaf_value. Mặc định 2.
   >-m, --multi_ln        In ra normal brackets trên nhiều dòng.
   >-e, --epsilon         Giữ lại epsilon.
   >-a, --assoc_disabled  Không enforce left/right associativity.
   >-w, --whole           Đọc toàn bộ file input thay vì từng dòng (đối với file nhỏ)```

<h2>Cách chạy module Lexer</h2>

1. Tải và cài đặt Python bản 3.12 trở lên https://www.python.org/downloads/.
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

<h2>Cấu trúc project</h2>

-	input: chứa các file code đầu vào (*.vc)
-	output:  chứa các file đầu ra tương ứng (*.vcps/vctok)
-	lexer: module lexer, bao gồm:
      -	__main__.py: Chứa hàm main() và lex_analyze() được gọi khi module chạy, cung cấp giao diện CLI.
      +	lexer_builder.py: Chứa LexerBuilder và các hàm dùng để phân tích từng dòng trong file .dat để từ đó xây dựng lexer.
      +	lexer.py: Định nghĩa Lexer, hàm is_newline() hỗ trợ xuống dòng..
      +	state.py: Định nghĩa các lớp trạng thái.
      +	state_attributes.py: Định nghĩa các lớp thuộc tính của state (Escape, Token).
      +	lexer_result.py: Định nghĩa đầu ra của lexer (LexicalResult, LexicalError, Location, Position).
      +	lex.dat: Khai báo thông tin dùng để xây dựng lexer cho ngôn ngữ VC. Format và cách thức sử dụng được comment và mô tả ngay trong file.
-	parser: module parser, bao gồm:
      +	__main__.py: Chứa hàm main()được gọi khi module chạy, cung cấp giao diện CLI.
      +	 parser.builder.py: Chứa ParserBuilder là một Parser Generator.
      +	grammar.dat: Dữ liệu ngữ pháp cho ParserBuilder.
      +	table.dat: Dữ liệu bảng trạng thái cho ParserBuilder.
      +	parser.py: Chứa Parser (kế thừa ParserBuilder) và logic của LL(1).
      +	types: Định nghĩa các loại Symbol và Production, cùng một số hàm tiện ích
      +	ast: module ast, chứa các file ast.py, node.py, brackets.py, epsilon.py, associativity.py gồm các data types và logic cần thiết để xây dựng, hậu xử lý và format output.
-	README.md: Cách chạy code và một số thông tin cơ bản.
