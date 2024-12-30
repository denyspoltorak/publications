I've spent some time looking for a way to generate the HTML table of contents for the book I've uploaded to Leanpub to show it on the book's page. Finally solved through the following steps:

0. Your epub book was created with Calibre and has a table of contents
1. Open the epub file with Calibre's ebook viewer
2. Right-click in the viewer window and choose table of contents from the menu
3. Right-click on the table of contents and copy it to clipboard
4. Save the ToC as toc.txt
5. Run `toc_to_html.py toc.txt toc.html` to get the HTML ToC
