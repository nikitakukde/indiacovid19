#!/usr/bin/env python3

# Copyright (c) 2020 Susam Pal
# Licensed under the terms of the MIT License.

# This software is a derivative of the original makesite.py available at
# <https://github.com/sunainapai/makesite>. The license text of the
# original makesite.py is included below.

# The MIT License (MIT)
#
# Copyright (c) 2018 Sunaina Pai
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.



import datetime
import os
import re
import shutil
import sys

from py import data, plot


def fread(filename):
    """Read file and close the file."""
    with open(filename, 'r') as f:
        return f.read()


def fwrite(filename, text):
    """Write content to file and close the file."""
    basedir = os.path.dirname(filename)
    if not os.path.isdir(basedir):
        os.makedirs(basedir)
    with open(filename, 'w') as f:
        f.write(text)


def log(msg, *args):
    """Log message with specified arguments."""
    sys.stderr.write(msg.format(*args) + '\n')


def render(template, **params):
    """Replace placeholders in template with values from params."""
    return re.sub(r'{{\s*([^}\s]+)\s*}}',
                  lambda match: str(params.get(match.group(1), match.group(0))),
                  template)


def case_links():
    prev_month = None
    months = []
    for date in data.dates:
        curr_month = date[:7]
        if curr_month != prev_month:
            months.append(curr_month)
        prev_month = curr_month

    out = []
    for month in months:
        text = datetime.datetime.strptime(month, '%Y-%m').strftime('%b')
        out.append(
            '<span>[&nbsp;<a href="#{}">{}</a>&nbsp;]</span>'
            .format(month, text)
        )
    return '\n'.join(out) + '\n'


def case_head(month):
    """Create HTML to display table heading for case numbers in a table."""
    th_date = datetime.datetime.strptime(month, '%Y-%m').strftime('%b&nbsp;%Y')
    out = [
        '  <tr id="{}">'.format(month),
        '    <th class="date"><a href="#{}">Dates ({})</a></th>'
        .format(month, th_date),
        '    <th class="total">Total Cases</th>',
        '    <th class="total">New Cases</th>',
        '    <th class="total">Growth</th>',
        '    <th class="active">Active Cases</th>',
        '    <th class="cured">Cured Cases</th>',
        '    <th class="death">Death Cases</th>',
        '    <th class="ref">Ref.<sup><a href="#footnote1">*</a></sup></th>',
        '  </tr>',
    ]
    return '\n'.join(out) + '\n'


def case_data(entry):
    (date, total, new, growth, active, cured, deaths, refs) = entry

    ref_date = refs[0][1]
    ref_link = refs[0][2]

    if growth == -1:
        growth = '-'
    else:
        growth = '{:+.0f}%'.format(100 * (growth - 1))

    out = [
        '  <tr id="{}">'.format(date),
        '    <td class="date"><a href="#{}">{}</a></td>'.format(date, date),
        '    <td class="total">{}</td>'.format(total),
        '    <td class="total">{:+}</td>'.format(new),
        '    <td class="total">{}</td>'.format(growth),
        '    <td class="active">{}</td>'.format(active),
        '    <td class="cured">{}</td>'.format(cured),
        '    <td class="death">{}</td>'.format(deaths),
        '    <td class="ref"><a href="{}">{}</a></td>'.format(
             ref_link, ref_date),
        '  </tr>',
    ]
    return '\n'.join(out) + '\n'


def case_rows():
    """Create HTML to display row of case numbers in a table."""
    prev_month = None
    out = ''
    for i, entry in enumerate(zip(data.dates,
                                  data.total_cases,
                                  data.total_diff,
                                  data.total_growth,
                                  data.active_cases,
                                  data.cured_cases,
                                  data.death_cases,
                                  data.refs)):
        curr_month = entry[0][:7]
        if curr_month != prev_month:
            out += case_head(curr_month)
        out += case_data(entry)
        prev_month = curr_month
    return out


def main():
    """Render the home page."""
    # Copy static files.
    if os.path.isdir('_site'):
        shutil.rmtree('_site')
    shutil.copytree('static', '_site')
    shutil.copy('indiacovid19.json', '_site')

    # Load COVID-19 data.
    data.load()

    # Plot graphs.
    log('Rendering linear plot ...')
    plot.all_cases_linear()
    log('Rendering logarithmic plot ...')
    plot.all_cases_logarithmic()
    log('Rendering bar plot ...')
    plot.new_cases()

    # Render home page.
    log('Rendering home page ...')
    layout = fread('layout/index.html')
    output = render(layout, case_links=case_links(), case_rows=case_rows())
    fwrite('_site/index.html', output)
    log('Done')


if __name__ == '__main__':
    main()
