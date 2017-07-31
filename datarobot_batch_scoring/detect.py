import math
import re


class Detector(object):

    frequency_table = None
    non_delimiter_re = re.compile('[\w]', re.UNICODE)
    buff_size = 1024 * 2048

    def __init__(self):
        self.frequency_table = {}

    def increment(self, char, lines):
        if char not in self.frequency_table:
            self.frequency_table[char] = {}
        if lines not in self.frequency_table[char]:
            self.frequency_table[char][lines] = 0

        self.frequency_table[char][lines] += 1

    def detect(self, sample):
        lines_analyzed = self.get_sample(sample)
        return self.analyze(lines_analyzed)

    def get_sample(self, sample, sample_lines=20, quotechar='"'):
        enclosed = False
        actual_lines = 1

        # raise Exception("Sample size %d" % len(sample))

        for idx, ch in enumerate(sample):
            if actual_lines >= sample_lines:
                break
            prev = sample[idx-1] if idx else None
            next = sample[idx+1] if (idx + 1) < len(sample) else None

            if ch == quotechar:
                if enclosed and next != quotechar:
                    enclosed = False
                elif not enclosed:
                    enclosed = True
            elif not enclosed and (ch == '\n' and prev != '\r' or ch == '\r'):
                actual_lines += 1

            elif not enclosed and not self.non_delimiter_re.match(ch):
                self.increment(ch, actual_lines)

        return actual_lines

    def analyze(self, lines_analyzed):
        candidates = []
        for delim, freq in list(self.frequency_table.items()):
            deviation = self.deviation(freq, lines_analyzed)

            if float(0.0) == deviation:
                candidates.append(delim)
        return candidates
            # freq struct {'': {0:0}}

    def mean(self, line_freq, lines_analyzed):
        """

        :param line_freq: dict[int]int
        :param lines_analyzed: int
        :return: int
            mean value of all characters appeared at sample
        """
        freqs = list(line_freq.values())[:lines_analyzed]
        return sum(freqs) / lines_analyzed

    def deviation(self, line_freq, lines_analyzed):
        lines_to_account = lines_analyzed - 1

        average = self.mean(line_freq, lines_to_account)
        frequencies = list(line_freq.values())[:lines_to_account]

        squares = map(lambda frequency: (float(average) - frequency) ** 2,
                      frequencies)

        return math.sqrt(sum(squares) / (lines_to_account - 1))
