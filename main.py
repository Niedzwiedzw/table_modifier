import typing as t
from pprint import pprint
from dataclasses import dataclass, field

from PIL import Image, ImageDraw, ImageFont
import pytesseract

NOISE_CHARACTERS = [
    '|'
]


def dbg(value: t.Any) -> t.Any:
    print(value)
    return value

@dataclass
class TextOccurrence:
    occurrence_id: int

    image: Image
    drawer: ImageDraw
    text: str

    top: int
    left: int
    height: int
    width: int

    word_num: int
    page_num: int
    par_num: int
    line_num: int
    block_num: int
    level: int

    conf: int

    @property
    def font_size(self):
        return int(1.3 * self.width / len(self.text))

    @property
    def font(self):
        return ImageFont.truetype('arial.ttf', self.font_size)

    def __post_init__(self):
        self.top = int(self.top)
        self.left = int(self.left)
        self.height = int(self.height)
        self.width = int(self.width)
        self.word_num = int(self.word_num)
        self.page_num = int(self.page_num)
        self.par_num = int(self.par_num)
        self.line_num = int(self.line_num)
        self.block_num = int(self.block_num)
        self.level = int(self.level)
        self.conf = int(self.conf)

    @property
    def rectangle(self):
        return self.left, self.top, self.left+self.width, self.top+self.height

    def substitute(self, text: str):
        self.drawer.rectangle(self.rectangle, 'white')
        self.drawer.text((self.left, self.top), str(self.occurrence_id), 'red', font=self.font)


@dataclass
class ImageExtractor:
    image: Image
    drawer: ImageDraw = field(init=False)

    occurrences: t.List[TextOccurrence] = field(default_factory=list, init=False)

    def __post_init__(self):
        self.drawer = ImageDraw.Draw(self.image)
        self.occurrences = image_data(self.image, self.drawer)

    def show(self):
        self.image.show()


def image_data(image: Image, drawer: ImageDraw) -> t.List[TextOccurrence]:
    data = pytesseract.image_to_data(image)
    data = [line.split() for line in data.split('\n') if line.strip()]
    header, values = data[0], data[1:]

    all_occurances = []

    for value_line in values:
        json_data = {}
        for key, value in zip(header, value_line):
            json_data[key] = value

        if 'text' in json_data.keys() and json_data['text'] not in NOISE_CHARACTERS:
            all_occurances.append(json_data)

    return [TextOccurrence(
        image=image,
        drawer=drawer,
        occurrence_id=index,
        **occurrence
    ) for index, occurrence in enumerate(all_occurances)]


if __name__ == '__main__':
    filename = './plan.jpg'
    imageobj = Image.open(filename).convert('RGBA')

    extractor = ImageExtractor(imageobj)

    for occurrence in extractor.occurrences:
        occurrence.substitute('DUPA DUPA')

    extractor.show()
    extractor.image.save('output.png', 'PNG')
