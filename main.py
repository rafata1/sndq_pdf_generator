from io import BytesIO

from flask import Flask, request, send_file
import pdfkit

app = Flask(__name__)

path_wkhtmltopdf = "/usr/bin/wkhtmltopdf"

def generate_invoice_content(ledgers):
    res = ''
    for ledger in ledgers:
        code = ledger['code']
        name = ledger['name']
        res = res + f'<p style="padding: 10px; font-weight: bold;">{code} - {name}</p>' + '\n'
        allocations = ledger['cost_allocations']
        allocations_table = generate_allocations_table(allocations)
        res = res + allocations_table + '\n'

    return res


def generate_allocations_table(allocations):
    res = ''
    for allocation in allocations:
        res = res + f'''
        <tr>
            <td align="left">{allocation['invoice_date']}</td>
            <td align="left">{allocation['invoice_number']}</td>
            <td align="left">{allocation['supplier_name']}</td>
            <td align="left">{allocation['description']}</td>
            <td align="right">&euro;{allocation['vat_amount']}</td>
            <td align="right">&euro;{allocation['total']}</td>
        </tr>
        '''
    return f'''
    <table style="margin-top: 5%; border: 0;" width="100%">
    {res}
    </table>
    '''




@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    # Retrieve data from the request
    data = request.get_json()

    building = data["building"]

    building_name = building['name']
    company_number = building['company_number']
    address_line_1 = building['address_line_1']
    address_line_2 = building['address_line_2']
    date_start = building['date_start']
    date_end = building['date_end']
    sum_total_amount = building['sum_total_amount']
    sum_vat_amount = building['sum_vat_amount']
    pagination = building['pagination']
    current_page = pagination['current_page']
    total_page = pagination['total_page']
    export_date = building['export_date']

    ledgers = building['ledgers']
    content = generate_invoice_content(ledgers)

    html_content = f'''
    <html>
    <head>
    </head>
    <body style="margin-left: 20%; margin-right: 20%; font-family: 'Helvetica', sans-serif;">
    <div style="display: flex;">
        <div style="width: 33.33%" align="left">
            <h3>{building_name}</h3>
            <p>{company_number}</p>
            <p>{address_line_1}</p>
            <p>{address_line_2}</p>
        </div>
        <div style="width: 33.33%" align="center">
            <h3>Facturenlijst - grootboekrekening</h3>
            <p>{date_start} - {date_end}</p>
        </div>
        <div style="width: 33.33%" align="right">
            <h3>{export_date}</h3>
            <p>Pagina {current_page} van {total_page}</p>
        </div>
    </div>
    
    <!--column header-->
    <table style="margin-top: 5%; border: 0;" width="100%">
        <tr>
            <td style="padding: 10px; font-weight: bold;" align="left">Datum</td>
            <td style="padding: 10px; font-weight: bold;" align="left">Factuurnr.</td>
            <td style="padding: 10px; font-weight: bold;" align="left">Leverancier.</td>
            <td style="padding: 10px; font-weight: bold;" align="left">Omschrijving</td>
            <td style="padding: 10px; font-weight: bold;" align="right">BTW</td>
            <td style="padding: 10px; font-weight: bold;" align="right">Totaal</td>
        </tr>
    </table>
    <hr>
    
    {content}
    
    <!--footer-->
    <hr>
    <table style="margin-top: 5%; border: 0;" width="100%">
        <tr>
            <td style="font-weight: bold;" align="left">Totaal</td>
            <td style="width: 100%"></td>
            <td style="font-weight: bold;" align="right">&euro;{sum_vat_amount}</td>
            <td style="font-weight: bold;" align="right">&euro;{sum_total_amount}</td>
        </tr>
    </table>
    </body>
    </html>
    '''

    pdf_bytes = pdfkit.from_string(html_content, False, configuration=pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf))
    pdf_io = BytesIO(pdf_bytes)
    return send_file(pdf_io, download_name="invoice.pdf", as_attachment=True)


if __name__ == '__main__':
    app.run()
