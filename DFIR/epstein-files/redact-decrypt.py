import pikepdf

def strip_redactions(input_pdf, output_pdf):
    # Open the leaky PDF
    with pikepdf.open(input_pdf) as pdf:
        for page in pdf.pages:
            # The 'Contents' of a page is a stream of instructions
            # (e.g., 'Draw line', 'Show text', 'Fill rectangle')
            if '/Contents' in page:
                if '/Annots' in page:
                    del page.Annots
                    print(f"Deleted annotation layer on {page}")

        # Save as a new file. pikepdf automatically repairs 
        # the xref table (the map) that caused the 'blank page' error earlier.
        pdf.save(output_pdf)
        print(f"Successfully cleaned! Open {output_pdf} to view.")

strip_redactions('efta5711.pdf', 'EFTA00005711_FIXED.pdf')
