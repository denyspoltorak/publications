# Guide on converting a Google Docs document into an eBook (well-structured PDF and EPUB files)

While it is convenient to write a book in Google Docs, transforming it into a high-quality eBook is complicated. Please find below the steps which you should take to make a pair of PDB and EPUB files from a Google Docs document using free software.

## Why Google Docs

I used Google Docs for writing a compendium which contained hundreds of pages, hundreds of diagrams, and thousands of cross-links.

### Benefits

- Online collaboration
- Decent UX
- Decent stability (few bugs, no data corruption)
- Performance (Google Docs seems to be faster than LibreOffice Writer)
- Instant backup
- You probably don't need to learn it

### Drawbacks

- Supports only basic editing
- Exporting is basic as well
- No integration with version control systems
- Unavailable offline

### The troubles you may encounter

- Google Docs has a hard time saving the table of contents into a PDF (as an outline) or EPUB file. Older versions did not generate it at all, which the newer ones may be buggy and provide next to no control over the structure of the table of contents.
- The resulting EPUB is not optimized. It may take too long to open and section breaks may be at the wrong granularity level.

### Use specialized software

It makes sense to rely on specialized tools:

- Google Docs for editing and collaboration
- Calibre for conversion to EPUB
- LibreOffice for conversion to PDF

## Exporting from Google Docs to LibreOffice Writer

Even though Google Docs and LibreOffice Writer are about the same thing, they differ in many details. I suppose that you have perfected your book in Google Docs and now want it to look the same in the output PDF file.

So you just go to `File -> Download -> OpenDocument Format (.odt)` in your Google Docs, wait for a while, open the downloaded document with LibreOffice and compare it to the original. I looked at the lengths of the documents - they should match. If they don't, you should probably check the length of every chapter to find the differences. A few hints are below:

### Fonts

The Google Docs set of fonts differs from that in OpenOffice Writer. I used Oswald in the explanation sections of my book only to find out that LibreOffice Write silently replaces it with a default font.

Therefore, please check all kinds of text styles which you use throughout your book. If anything looks wrong, you may have to download a corresponding font from Google and install it on your computer.

### Document structure

Google Docs uses header text style for chapters and sections. With LibreOffice Writer styles and structure are separate.

You will need to:

- open the "Styles and Formatting" right-side panel and right-click and `Modify...` the header styles there or
- right-click on each kind of header in your document and choose `Paragraph -> Edit Style...` to set up the outline levels.
The outline levels are set up in the `Outline & List` paragraph style tab.

For example, in my book there are:

1. Title style for book parts - it gets outline level 1
2. Heading 1 style for chapters - outline level 2
3. Heading 2 style for groups of sections - outline level 3
4. Heading 2 style for individual sections - outline level 4

Please be aware that now your book's title or blank lines from the title page may appear as stray chapters in the table of contents, unless you change their styles to default and set up their font sizes manually.

### Orphaned lines

Google Docs prevents single lines of text from appearing at the top or bottom of the page. LibreOffice Writer has two controls for that: `Orphan control` and `Widow control`. Both are in the `Text Flow` tab of the paragraph style dialog.

You have to enable both of them for the `default paragraph style`. Please note that they are already enabled for headings.

There is also a subtle difference in the logic of the feature: while Google Docs keeps a header, diagram, and the following caption line together, LibreOffice Writer does not consider them to be a single paragraph, thus you may see a caption separated from its diagrams or a section header together with a diagram separated from the section's text. Fixing that will likely require manual changes which may be as simple as inserting a blank line before every diagram with a caption.

### Tables

Google Docs seems to generate tables with no padding. While the tables look good in Google Docs, in LibreOffice Writer the spacing between cells is smaller than the spacing between lines of text inside a cell.

Thus you may need to increase padding in the `Table Properties -> Borders` dialog for each table in your document. There seems to be no easy way to select all the tables - you'll have to edit each of them manually.

### Transparency

I used transparency to reduce the contrast of the background image on the title page of my book. LibreOffice Writer does not support transparency for images, only for page areas. I had to delete the cover image and re-insert it through `Page Style -> Area -> Image` to make it semi-transparent via `Page Style -> Area -> Transparency`.

### Bullets and fonts

If you use multiple fonts in a list, the list's bullets will differ in size. You'll need to left-click a bullet (this selects all the bullets in the list) and choose a font which will apply to all the bullets.

### Known bugs

There are several LibreOffice Writer bugs (as of 7.3.7.2) that cause inconveniences:

- Recovery of a document after a crash may corrupt suggestions - additions become deletions. This is a point against offline collaboration via ODT files.
- Autosave (recovery backup) cannot be disabled via `Options -> Load/Save -> General -> Save AutoRecovery information`. This is really annoying for large documents as the saving takes half a minute and happens every 10 minutes.
- `Paragraph Style -> Text Flow -> Keep with next paragraph` setting is not applied when a document is loaded. Opening the style dialog for a header and just pressing OK will reformat the document and may change its number of pages and the PDF output.

## Exporting to a PDF

This is straightforward:

- Run `File -> Export As -> Export as PDF...` in LibreOffice Writer.
- Be sure that the `Archive (PDF/A, ISO 19005)` box is checked.
- The `Export outlines` checkbox is responsible for creation of the table of contents.

Now you have your PDF with a nice table of contents!

## Making a EPUB

This part is complicated.

You will probably want to make a copy of your document as the steps below involve destructive modifications.

### Get rid of the title page

The EPUB includes the cover as a stand-alone image. Therefore you should delete the cover page from your document to avoid its being duplicated. Which is not that easy because the title page's properties differ from those of other pages, therefore merely deleting the cover page's text and image does not work - the second page becomes the new title page.

I found the following workaround:

- Delete the contents of your title page. Your second page will become your title page.
- Select `Format -> Title Page... -> Make Title Pages -> Insert new title pages`. Press OK - that should insert a blank default-style title page in front of the document
- Now delete the newly inserted blank lines to pull the text from your second page into the first page.
- Save the updated document.

### Generate the cover image

Now you need to create the cover (printout of your title page) for your EPUB. There are two ways:

- KISS: Make a screenshot of your title page in Google Docs or LibreOffice Writer.
- The knightly path: Extract it from the PDF file generated in the previous section. Assuming you are on Linux, run `pdftoppm -singlefile -png YourBook.pdf > Cover.png`

### Create the EPUB

You will need Calibre. Install it.

- Open your ODT file without the title page with Calibre (that should be possible through right-clicking the file and choosing `Open with other application`).
- Right-click on the newly created book in Calibre's library (its main page) and select `Edit metadata -> Edit metadata individually`.
    - Set the book's cover from the image generated in the previous step.
    - Fill in the title and author(s).
    - You can add tags, but I don't know if they appear in the published book, or are internal to Calibre.
    - Apply the changes.
- Right-click on your book. `Convert books -> Convert individually`.
    - Choose ODT as input and EPUB as output format.
    - Fonts tab of the `Look and Feel` dialog:
        - Check `Embed all fonts`
        - Check `Subset all embedded fonts`
    - There is some magic under the `Structure detection` dialog:
        - `Detect chapters` works with `//*[name()='h1' or name()='h2' or name()='h3' or name()='h4']` - This probably is related to the table of contents. Calibre's table of contents is limited to 3 levels, however.
        - `Insert page breaks before` should detect every kind of section if we want every section to appear on a new page: `//*[name()='h1' or name()='h2' or name()='h3' or name()='h4']`.
    - The `Table of Contents` dialog also needs your attention:
        - Change the `Number of links to add` to a big number like 500.
        - The levels are required for a multi-level (hierarchical) table of contents:
        - Set `Level 1 TOC` to `//*[name()='h1']`
        - Set `Level 2 TOC` to `//*[name()='h2']`
        - Set `Level 3 TOC` to `//*[name()='h3']`
        - Check `Manually fine-tune the ToC after conversion`.
    - Click OK and wait for a couple of minutes.
    - Enjoy the preview of your table of contents. You can edit it manually or delete and regenerate it with the buttons on the right side of the dialog.
        - Alternatively, you can delete the generated table of contents by pressing `Ctrl+A` and `del` and create a new full-depth table of contents by using the `Create table of contents from all headers` button. This allows for making a 4-level table of contents and also adds introductory sections.
    - If you work on the table of contents for a couple of minutes, there will appear a pop-up warning about a ToC creation timeout. It is safe to ignore.
- Right-Click on your book. Choose `Open containing folder`. Enjoy the EPUB you've created!

### Issues with Calibre's EPUB

There are a couple of troubles with the Calibre's output:

- It uses `<class="calibre">` in a non-standard place which results in errors from EPUB validation tools. If your publisher insists on fixing the errors (PublishDrive does), you should:
    - Install Sigil.
    - Open the EPUB with Sigil.
    - Find ` class="calibre">` and replace it with `>` throughout the EPUB contents (`All HTML Files`).
- Lists are not well-aligned. Fixing that requires knowledge of CSS.

## Publish the book

I tried Leanpub (PDF and EPUB) and PublishDrive (EPUB only).

PublishDrive is stringent on errors. You will need to fix the EPUB created by Calibre (see above).

Leanpub accepts everything, but it has a couple of peculiarities:

### Generating the table of contents for Leanpub

Leanpub expects you to generate the table of contents of your book as a HTML list. You will need to do the following:

- Open your EPUB (3 ToC levels) or PDF (4 ToC levels but it may take forever to open) file with Calibre's E-book viewer.
- Right-click on the table of contents in the viewer and select `Copy Table of Contents to clipboard`.
- Paste the table of contents into your favorite plain text editor and save it as a TXT file. You may also edit the contents if needed.
- Download [my converter](https://github.com/denyspoltorak/publications/blob/main/tools/toc_to_html.py) (a tiny Python script) and run it: `./toc_to_html.py toc.txt toc.html`
- Open the generated HTML file with a plain text editor and copy-paste its contents into your book's Leanpub page.

### Generating a sample chapter

You will probably want Leanpub to offer prospective readers to download a sample chapter from your book. However, that requires you to prepare the corresponding PDF and EPUB files:

- Clone the book in Google Docs
- Edit the cover
- Delete everything except the table of contents, the chapter you will use for promotion and, probably, a few appendixes.
- Unlink any cross-references to the deleted chapters throughout the remaining text, including the table of contents.
- Download the sample as ODT.
- Repeat all the steps which you did for your book:
    - Fix the ODT with LibreOffice Writer.
    - Convert it to PDF.
    - Convert it to EPUB with Calibre.

That's it. Enjoy your book.

Please feel free to [contact me](https://www.linkedin.com/in/denyspoltorak/) if you have any improvements for this instruction.













