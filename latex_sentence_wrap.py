import sublime
import sublime_plugin
# import string


def beginning_of_latex_sentence(view, region):
    # Start at beginning of region
    pt = region.begin()

    # Define possible beginning-of-sentence strings
    begin_strings = []

    # End of sentence punctuation, maybe followed by "$", ")", or "''", then
    # followed by at least 1 space and a capital letter, number, "$" or "(""
    begin_strings.append(r"[.?!][$)]?('')?\s+[A-Z0-9$(]")

    # End of sentence punctuation followed at least 1 space
    # and by "\citet", "citeauthor", "emph", "textbf"
    begin_strings.append(r"[.?!]\s+\\(?=citet|citeauthor|emph|textbf)")

    # Double backslash followed by 0 or more spaces
    begin_strings.append(r"\\\\\s*")

    # New line followed by a capital letter or number
    begin_strings.append(r"^\s*$\s*[A-Z0-9]")

    # "{" followed by any character
    # begin_strings.append(r"\{.")

    # A lone "%" on a new line followed by any character
    begin_strings.append(r"^\s*%\s*$\s*.")

    # "\begin{...}" followed by a newline and then any character
    # NOT including "\"
    begin_strings.append(r"\\begin\{.*\}\s*[^\\]")

    # "\label{...}" followed by a newline and then any character
    begin_strings.append(r"\\label\{.*\}\s*.")

    # Newline followed by "\item [...]" and then any character
    begin_strings.append(r"$\s*\\item(\s*\[.*\])*\s*.")

    # Find beginning-of-sentence region
    prior_regions = [r for r in view.find_all('|'.join(begin_strings))
                     if r.begin() < pt]
    if prior_regions:
        begin_region = prior_regions[-1]

    # Return end of beignning-of-sentence region, offset by -1
    return begin_region.end() - 1

    # Debugging: return complete beginning-of-sentence region
    # return begin_region
    # return prior_regions


def end_of_latex_sentence(view, region):
    # Start at beginning of region
    pt = region.begin()

    # Define possible end-of-sentence strings
    end_strings = []

    # End-of-sentence punctuation followed by at least 1 space
    end_strings.append(r"[.?!]\s+")

    # End-of-sentence punctuation followed by "$" or )" and at least 1 space
    end_strings.append(r"(?<=[.?!])[$)]\s+")

    # End-of-sentence punctuation followed by "''" and at least 1 space
    end_strings.append(r"(?<=[.?!])''\s+")

    # Double backslash followed by 0 or more spaces
    end_strings.append(r"\\\\\s*")

    # Any character followed by a lone "%" on a new line
    end_strings.append(r".\s*$\s*%\s*$")

    # Any character followed by the beginning of a new environment,
    # end of the current environment, or item
    end_strings.append(r".\s*$\s*(\\begin|\\end|\\item)")

    # Any character followed by "}"
    # end_strings.append(r".\}")

    # Find end-of-sentence region
    end_region = view.find('|'.join(end_strings), pt)

    # Return beginning of end-of-sentence region
    return end_region.begin()

    # Debugging: return complete end-of-sentence region
    # return end_region


def expand_to_latex_sentence(view, region):
    # Get beginning of sentence
    begin = beginning_of_latex_sentence(view, region)

    # Get end of sentence
    end = end_of_latex_sentence(view, region)

    # Return a Region containing the sentence
    return sublime.Region(begin, end + 1)


def next_latex_sentence_on_new_line(view, edit, region):
    # Get end of current sentence
    current_end = end_of_latex_sentence(view, region)

    # Get beginning of next sentence
    next_begin = beginning_of_latex_sentence(
        view, sublime.Region(current_end + 1, current_end + 1)
    )

    # Check if there is a new line above the next sentence
    prior_newline = [r for r in view.find_all(r"\n")
                     if r.begin() >= current_end and r.begin() <= next_begin]
    if not prior_newline:
        # If so, insert new line
        view.insert(edit, next_begin, '\n')

        # Output region containing beginning of next sentence,
        # which is now offset by 1
        return sublime.Region(next_begin + 1, next_begin + 1)
    else:
        # Otherwise, output region containing beginning of next sentence
        return sublime.Region(next_begin, next_begin)


class ExpandSelectionToLatexSentenceCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        input_regions = self.view.sel()
        output_regions = []
        for r in input_regions:
            output_regions.append(expand_to_latex_sentence(self.view, r))

        self.view.sel().clear()
        for r in output_regions:
            self.view.sel().add(r)


class WrapLatexSentenceCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        input_regions = self.view.sel()
        output_regions = []
        for r in input_regions:
            output_regions.append(expand_to_latex_sentence(self.view, r))

        self.view.sel().clear()
        for r in output_regions:
            self.view.sel().add(r)
        self.view.run_command('wrap_lines_plus')


class NextLatexSentenceOnNewLineCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        input_regions = self.view.sel()
        output_regions = []
        for r in input_regions:
            output_regions.append(next_latex_sentence_on_new_line(self.view,
                                                                  edit, r))
        self.view.sel().clear()
        for r in output_regions:
            self.view.sel().add(r)


class LatexNelsonTestCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        begin = beginning_of_latex_sentence(self.view, self.view.sel()[0])
        end = end_of_latex_sentence(self.view, self.view.sel()[0])
        next_begin = beginning_of_latex_sentence(
            self.view, sublime.Region(end + 1, end+1)
        )
        # next_begin = self.view.find_by_class(end, True,
        #                                      sublime.CLASS_WORD_START)
        # next_begin = beginning_of_latex_sentence(self.view,
        #     sublime.Region(next_begin, next_begin))

        self.view.sel().clear()
        # self.view.sel().add(sublime.Region(begin, end + 1))
        # for r in begin:
        #    self.view.sel().add(r)
        # self.view.sel().add(end + 2)
        # self.view.sel().add(next_begin)
        self.view.sel().add(begin)
