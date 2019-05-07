#!./python

# Purpose: CGI script that generates a small MGI Header for a Lexicon or
# DeltaGen detail page.
#
# Notes: admittedly quick and dirty conversion from python WI to new
#	knockout_mice product and to hit front-end database rather than 
#	production-style database.

import sys
if '/usr/local/mgi/live/lib/python' not in sys.path:
	sys.path.insert(0, '/usr/local/mgi/live/lib/python')

import Configuration
import pg_db
import mgi_html
import cgi
import os
import re

###--- local config file + shared global config file ---###

localConfig = Configuration.Configuration('../Configuration')
globalConfig = Configuration.Configuration(
	os.path.join(localConfig['MGICONFIG'], 'web/GlobalConfig'))

###--- functions ---###

def initializeDatabaseConnection():
    user = globalConfig['DB_USER']
    password = globalConfig['DB_PASSWORD']
    server = globalConfig['DB_SERVER']
    database = globalConfig['DB_DATABASE_FE']

    pg_db.set_sqlLogin(user, password, server, database)
    pg_db.useOneConnection(1)

    try:
	results = pg_db.sql('''select value from database_info
		where name = 'built from mgd database date' ''', 'auto')
    except:
	raise Exception('Cannot read from %s..%s as user %s' % (
		server, database, user))
    return

def genMGIHeader(dataset, companyID):
    # Purpose: get the HTML that represents the MGI header for a Lexicon or
    #          Deltagen page.
    # Returns: string
    # Assumes: we can query the database using pg_db.sql()
    # Effects: queries the database using pg_db.sql()
    # Throws: propagates any exceptions raised by pg_db.sql()

    # pick up config options

    kmUrl = 'http://%s/knockout_mice/' % globalConfig['PY_HOST']
    fewi = globalConfig['FEWI_URL']
    mgihome = globalConfig['MGIHOME_URL']
    faqurl = globalConfig['FAQ_URL']
    webshare = globalConfig['WEBSHARE_URL']
    koLoc = localConfig['KO_DATA_DIR']

    # mouse specific data 
    markerKey           = 0
    markerID            = ""
    geneSymbol          = ""
    geneName            = ""
    alleleSymbol        = ""
    alleleID           = ""
    holder              = ""
    title               = ""

    # Links and locations
    geneDetailLink      = ""
    alleleDetailLink    = ""
    infoCell            = "&nbsp;"
    molBioLoc           = kmUrl + "deltagen/"
    dataDisplayType	= ""
    holderDisplayName	= ""
    
    # set dataset-specific values
    if dataset == "Deltagen":
        holder = "Deltagen"
        title = "Deltagen Knockout Mice<br>Phenotypic Data Summary"
        holderDisplayName = "Deltagen, Inc."
        dataDisplayType = "phenotypic data"

    elif dataset == "DeltagenMolBio":
        holder = "Deltagen"
        title = "Deltagen Knockout Mice<br>Molecular Biology Summary"
        holderDisplayName = "Deltagen, Inc."
        dataDisplayType = "molecular biology data"

    elif dataset == "Lexicon":
        holder = "Lexicon"
        title = "Lexicon Knockout Mice<br>Phenotypic Data Summary"
        holderDisplayName = "Lexicon Genetics, Inc."
        dataDisplayType = "phenotypic data"
    else:
        pass # exception for incorrect page; 

    # get data from the DB (assumes only one match, takes the first one)

    cmd = '''select mm.symbol as genesymbol, mm.name as genename, mm.marker_key,
    		aa.symbol as allelesymbol, aa.allele_key as allelekey,
		mm.primary_id as geneid, aa.primary_id as alleleid
	from marker mm, allele aa, marker_location ml, marker_to_allele mta
	where mm.marker_key = mta.marker_key
		and mta.allele_key = aa.allele_key
		and aa.company_id = '%s'
		and aa.holder = '%s'
		and ml.marker_key = mm.marker_key
		and ml.sequence_num = 1
	order by mm.symbol
	limit 1''' % (companyID, holder)

    results = pg_db.sql(cmd,'auto')

    if (len(results) > 0):
        row = results[0]
        markerID        = row['geneID']
        markerKey       = row['marker_key']
        geneSymbol      = row['geneSymbol']
        geneName        = row['geneName']
        if row['alleleSymbol'] != None:
            alleleSymbol = mgi_html.doSubSupTags(row['alleleSymbol'])
        if row['alleleID'] != None:
            alleleID = row['alleleID']

        geneDetailLink = fewi + "marker/" + markerID
        alleleDetailLink = fewi + "allele/" + alleleID

    # Now that we have the data from the database, fill in the info cell if needed
    if dataset == "Deltagen":
        
        # Premake the three anchors
        molBioLink = '<a href="' + molBioLoc + companyID + \
            '_MolBio.html" target="_top">Molecular Biology</a>'
        pdfLink = '<a href="deltagen/deltagenprotocols.pdf' + \
            '" target="_top">Phenotyping Protocols (.pdf)</a>'
        dlDataFileLink = '<a href="' + kmUrl + \
            'data/zipped/%s.zip">Download Data Files</a>' % markerID.replace(':','')
        aboutDlLink = '<a href="' + mgihome + \
            'other/AboutTheDownload.shtml"' + \
            'target="_top"> About the download</a>'
        
        infoCell = '\n'.join( [
            '<TABLE ALIGN="left" BORDER=0 CELLSPACING=0 CELLPADDING=4 WIDTH="100%">',
            '<TR><TD>%s</TD>' % molBioLink,
            '<TD>%s</TD>' % pdfLink,
            '<TD>%s</TD>' % dlDataFileLink,
            '<TD>%s</TD>' % aboutDlLink,
            '</TR></TABLE>'])

    # Create the output page
    page = '\n'.join([
      '<html>',
      '  <head>',
      '    <title>Deltagen and Lexicon Knockout Mice</title>',
      '    <LINK REL="stylesheet" HREF="%scss/mgi.css"> ' % webshare,
      '    <style>a:link { text-decoration: none; }</style>',
      '  </head>',
      '  <body>',
      '  <div id="mgiFrameHeader"> ',
      '  <table width="100%"><tr><td style="width:200px"> ',
      '    <a href="%shomepages" target="_top"> ' % mgihome,
      '    <img src="%simages/mgi_logo.gif" border=0></a> ' % webshare,
      '    <br/> ',
      '    <span style="font-size:10px; color:#002255;" > ',
      '    <a class="logoFooter" href="%shomepages" target="_top">&nbsp;Home</a>&nbsp;' % mgihome,
      '    |&nbsp;<a class="logoFooter" href="%sprojects/aboutmgi.shtml" target="_top">About</a>&nbsp;' % mgihome,
      '    |&nbsp;<a class="logoFooter" href="%shomepages/help.shtml" target="_top">Help</a>&nbsp;' % mgihome,
      '    |&nbsp;<a class="logoFooter" href="%sFAQ.shtml" target="_top">FAQ</a></span>' %  faqurl,
      '  </td> ',
      '  <td><div class="mgiFrameHeaderText">%s</div></td> ' % title,
      '  </tr></table> ',
      '  </div> ',
      '    ',
      '<table width="100%"  border="0" cellspacing="0" cellpadding="4" bgcolor="#FFFFFF">',
      '  <tr >',
      '    <td width="5%">&nbsp;</td>',
      '    <td nowrap width="25%"><span class="label">Gene symbol:</span> ',
      '      <a href="%s" target="_top">' % geneDetailLink,
      '      %s</a></td>' % geneSymbol, 
      '    <td><span class="label">Gene name:</span> %s</td>' % geneName,
      '  </tr>',
      '  <tr>',
      '    <td width="5%">&nbsp;</td>',
      '    <td nowrap width="25%"><span class="label">Allele symbol:</span> ',
      '      <a href="%s" target="_top">' % alleleDetailLink,
      '      %s</a></td>' % alleleSymbol, 
      '    <td>%s</td>' % infoCell,
      '  </tr>',
      '  <tr>',
      '    <td colspan="3"><div align="center"><span class="disclaimer">',
      '     This %s and presentation format were ' % dataDisplayType,
      '     provided by %s ' % holderDisplayName,
      '     and are presented as received. MGI has not verified the content or format ',
      '     of the material.<BR> ',
      '    The MGI database may have additional phenotypic or expression data.',
      '    Follow the Allele Symbol and Gene Symbol links above for more information.',
      '  </span></div>', 
      '    </td>',
      '  </tr>',
      '</table>',
      '<HR>',
      '</body></html>'])

    return page
        
def validateParameters(dataset, companyID):
	# ensure that the submitted parameters are valid and not problematic
	# (as far as preventing SQL injection and XSS attacks)

	# There are only three valid values for dataset - must be one of 'em.
    
	if dataset not in [ "Deltagen", "DeltagenMolBio", "Lexicon" ]:
		raise Exception('Invalid dataset parameter')

	# The companyID must be an integer number between 10 and 9999.
 
	p = re.compile('^[0-9]{2,4}$')
	match = p.match(companyID)
	if not match:
		raise Exception('Invalid companyID parameter')
	return

###--- main logic ---###

def main():

    input = cgi.FieldStorage()

    dataset = 'Lexicon'
    companyID = ''

    if input.has_key('dataset'):
        dataset = input['dataset'].value
    else:
        #  Exception: no dataset
        pass
        
    if input.has_key('companyID'):
        companyID = input['companyID'].value
    else:
        #  Throw exception with "no project id/company id passed in" message
        pass

    validateParameters(dataset, companyID)
    initializeDatabaseConnection()
    page = genMGIHeader(dataset, companyID)
    print page


###---  CGI Entry point ---###

print 'Content-type: text/html'
print
try:
    main()
except:
    print '''<html><head><title>MGI - Error</title></head>
    	<body>
	An error occurred when generating the header for this page:<br/>
	<blockquote>
	<i>%s</i> : %s
	</blockquote>
	</body></html>''' % sys.exc_info()[0:2]
