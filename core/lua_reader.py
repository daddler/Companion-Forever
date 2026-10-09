"""
Ein Leser für die Tabellen, die WoW in SavedVariables schreibt.

Bis 5.1 las die App aus `WeintCodex.lua` nur die eigene Zustellung
(`WeintCompanionDB`), und dafür reichte die Klammersuche in
`core/lua_table.py`. Der Bestand aller Charaktere (`inventory` in
`WeintCodex_SavedData`) ist dagegen eine echte, verschachtelte Tabelle
- Charakter, Taschen, Gegenstandsnummer, Anzahl -, und sie mit
regulären Ausdrücken auszulesen hiesse, sie beim ersten Namen mit
einer Klammer darin falsch zu lesen.

Gelesen wird **nur, was WoW selbst schreibt**: Tabellen, Zeichenketten,
Zahlen, `true`/`false`/`nil` und die `-- [n]`-Kommentare hinter
Listeneinträgen. Kein Ausdruck wird ausgewertet, nichts ausgeführt -
die Datei liegt im Spielordner, und was dort steht, ist Eingabe, kein
Programm.

Eine Tabelle wird zu einem `dict`; die Listeneinträge ohne Schlüssel
bekommen ihre Lua-Nummern (1, 2, ...) als Schlüssel. Ob daraus eine
Liste wird, entscheidet der Aufrufer - eine Tabelle mit Lücken ist in
Lua keine Liste, und hier soll sie auch keine werden.
"""

from __future__ import annotations


class LuaReadError(ValueError):
    pass


_ESCAPES = {
    "n": "\n",
    "t": "\t",
    "r": "\r",
    "a": "\a",
    "b": "\b",
    "f": "\f",
    "v": "\v",
    "\\": "\\",
    '"': '"',
    "'": "'",
    "\n": "\n",
}


class _Reader:

    def __init__(self, text: str):

        self.text = text

        self.pos = 0

    # --------------------------------------------------

    def skip(self):

        text = self.text

        length = len(text)

        while self.pos < length:

            char = text[self.pos]

            if char in " \t\r\n":
                self.pos += 1
                continue

            if text.startswith("--", self.pos):

                if text.startswith("--[[", self.pos):

                    end = text.find("]]", self.pos + 4)

                    self.pos = length if end == -1 else end + 2

                else:

                    end = text.find("\n", self.pos)

                    self.pos = length if end == -1 else end + 1

                continue

            break

    def peek(self) -> str:

        self.skip()

        return self.text[self.pos] if self.pos < len(self.text) else ""

    def expect(self, char: str):

        if self.peek() != char:
            raise LuaReadError(
                f"Erwartet {char!r} an Stelle {self.pos}"
            )

        self.pos += 1

    # --------------------------------------------------

    def value(self):

        char = self.peek()

        if char == "{":
            return self.table()

        if char in "\"'":
            return self.string()

        if char == "[" and self.text.startswith("[[", self.pos):
            return self.long_string()

        if char == "-" or char == "." or char.isdigit():
            return self.number()

        for word, result in (("true", True), ("false", False), ("nil", None)):

            if self.text.startswith(word, self.pos):

                self.pos += len(word)

                return result

        raise LuaReadError(f"Unbekannter Wert an Stelle {self.pos}")

    def string(self) -> str:

        quote = self.text[self.pos]

        self.pos += 1

        out = []

        text = self.text

        while True:

            if self.pos >= len(text):
                raise LuaReadError("Zeichenkette ohne Ende")

            char = text[self.pos]

            if char == quote:
                self.pos += 1
                break

            if char == "\\":

                nxt = text[self.pos + 1:self.pos + 2]

                if nxt.isdigit():

                    digits = ""

                    index = self.pos + 1

                    while index < len(text) and len(digits) < 3 and text[index].isdigit():
                        digits += text[index]
                        index += 1

                    out.append(chr(int(digits)))

                    self.pos = index

                    continue

                out.append(_ESCAPES.get(nxt, nxt))

                self.pos += 2

                continue

            out.append(char)

            self.pos += 1

        #
        # WoW schreibt Bytes. Was als UTF-8 gemeint war (Umlaute in
        # Namen), steht nach chr() je Byte als Latin-1 da; zurück in
        # Bytes und als UTF-8 gelesen ist es wieder der Name.
        #

        raw = "".join(out)

        try:
            return raw.encode("latin-1").decode("utf-8")

        except (UnicodeEncodeError, UnicodeDecodeError):
            return raw

    def long_string(self) -> str:

        end = self.text.find("]]", self.pos + 2)

        if end == -1:
            raise LuaReadError("Lange Zeichenkette ohne Ende")

        value = self.text[self.pos + 2:end]

        self.pos = end + 2

        return value

    def number(self):

        start = self.pos

        text = self.text

        while self.pos < len(text) and text[self.pos] in "0123456789+-.eExXabcdefABCDEF":
            self.pos += 1

        token = text[start:self.pos]

        try:

            if token.lower().lstrip("-").startswith("0x"):
                return int(token, 16)

            try:
                return int(token)

            except ValueError:
                return float(token)

        except ValueError:

            raise LuaReadError(f"Keine Zahl: {token!r}") from None

    def table(self) -> dict:

        self.expect("{")

        result = {}

        index = 1

        while True:

            char = self.peek()

            if char == "}":
                self.pos += 1
                return result

            if char == "[" and not self.text.startswith("[[", self.pos):

                self.pos += 1

                key = self.value()

                self.expect("]")

                self.expect("=")

                result[key] = self.value()

            elif char.isalpha() or char == "_":

                start = self.pos

                while self.pos < len(self.text) and (
                    self.text[self.pos].isalnum() or self.text[self.pos] == "_"
                ):
                    self.pos += 1

                word = self.text[start:self.pos]

                if self.peek() == "=":

                    self.pos += 1

                    result[word] = self.value()

                else:

                    #
                    # Ein Listeneintrag, der mit einem Wort beginnt
                    # (true/false/nil). Zurück und als Wert lesen.
                    #

                    self.pos = start

                    result[index] = self.value()

                    index += 1

            else:

                result[index] = self.value()

                index += 1

            if self.peek() in ",;":
                self.pos += 1


def read_variable(text: str, name: str):
    """
    Den Wert von `name = ...` auf oberster Ebene, oder `None`, wenn die
    Datei ihn nicht enthält.

    `LuaReadError`, wenn er da ist, aber nicht lesbar - ein kaputter
    Spielstand ist etwas anderes als einer ohne diese Variable, und
    der Aufrufer soll beides unterscheiden können.
    """

    needle = f"{name} ="

    start = 0

    while True:

        found = text.find(needle, start)

        if found == -1:
            return None

        #
        # Nur am Zeilenanfang: `WeintCodex_SavedData` darf nicht in
        # `WeintCodex_SavedDataOld = ` gefunden werden, und ein Name
        # in einer Zeichenkette ist keine Zuweisung.
        #

        if found == 0 or text[found - 1] == "\n":
            break

        start = found + 1

    reader = _Reader(text)

    reader.pos = found + len(needle)

    return reader.value()
