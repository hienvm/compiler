from typing import Union


class Token:
    def __init__(self, *labels: str) -> None:
        """Lexical token.

        Args:
            labels: Các nhãn của token.
        """
        self.labels = set(labels)

    def isa(self, other: Union[str, set[str], 'Token']) -> bool:
        """Check xem token này có chứa các label của (hay nói cách khác là thỏa mãn) một Token khác hay không.

        Args:
            other (str | set[str] | Token): label, set[labels] hoặc Token khác

        Returns:
            bool: đúng nếu other là tập con của self, false nếu ngược lại
        """
        if isinstance(other, str):
            # VD: Token("literal", "float").isa("literal") -> True
            return other in self.labels
        elif isinstance(other, set):
            # VD: Token("literal", "float", "e_notation").isa({"e_notation", "float"}) -> True
            return self.labels.issuperset(other)
        elif isinstance(other, Token):
            # VD: Token("literal", "float", "e_notation").isa(Token("float")) -> True
            return self.labels.issuperset(other.labels)
        else:
            return False

    def __str__(self) -> str:
        s = ''
        for label in self.labels:
            s += label + ' '
        return s


class Escape:
    def __init__(self, old: str, new: str) -> None:
        """Chuỗi escape. Khi đến trạng thái được định nghĩa escape thì Lexer sẽ thay len ký tự cuối lexeme bằng xâu new_val.

        Args:
            old (str): xâu cũ
            new (str): xâu mới
        """
        self.old = old
        self.new = new
