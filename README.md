# lexical-analyzer
1. Mở cửa sổ dòng lệnh tại thư mục chính
2. Ném file code vào folder input để dùng tên file cho bước 3 (nếu không thì dùng đường dẫn absolute).
3. Chạy module lexer: `python -m lexer file_url_1 [file_url_2...]`
+ VD: python -m lexer sample.vc example_fib.vc example_gcd.vc
4. Xem kết quả tại folder output (đuôi .vctok)
* Để xem trợ giúp và các option khác: `python -m lexer -h`
