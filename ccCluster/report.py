# coding: utf8
'''
Created on May 9, 2016

@author: svensson
'''

import os
import sys
# reload(sys)
# sys.setdefaultencoding('utf8')
import html
import PIL.Image
import json
import time
import base64
import tempfile

# from workflow_lib.edna_kernel import markupv1_10

if sys.version.startswith('3'):
    unicode = str

# Report version
REPORT_VERSION = 1.0

class WorkflowStepReport(object):

    def __init__(self, stepType, stepTitle=""):
        self.imageList = None
        self.dictReport = {}
        self.dictReport["version"] = REPORT_VERSION
        self.dictReport["type"] = stepType
        self.dictReport["title"] = stepTitle
        self.dictReport["items"] = []

    def setTitle(self, stepTitle):
        self.dictReport["title"] = stepTitle


    def addInfo(self, infoText):
        self.dictReport["items"].append({"type": "info",
                                         "value": infoText})

    def addWarning(self, infoText):
        self.dictReport["items"].append({"type": "warning",
                                         "value": infoText})

    def startImageList(self):
        self.imageList = {}
        self.imageList["type"] = "images"
        self.imageList["items"] = []

    def endImageList(self):
        self.dictReport["items"].append(self.imageList)
        self.imageList = None

    def __createImageItem(self, pathToImage, imageTitle, pathToThumbnailImage=None,
                          thumbnailHeight=None, thumbnailWidth=None):
        item = {}
        item["type"] = "image"
        item["suffix"] = pathToImage.split(".")[-1]
        item["title"] = imageTitle
        im = PIL.Image.open(pathToImage)
        item["xsize"] = im.size[0]
        item["ysize"] = im.size[1]
        item["value"] = base64.b64encode(open(pathToImage, 'rb').read()).decode("utf-8") 
        if pathToThumbnailImage is None:
            if thumbnailHeight is not None and thumbnailWidth is not None:
                item["thumbnailSuffix"] = pathToImage.split(".")[-1]
                item["thumbnailXsize"] = thumbnailHeight
                item["thumbnailYsize"] = thumbnailWidth
                item["thumbnailValue"] = base64.b64encode(open(pathToImage).read())
        else:
            item["thumbnailSuffix"] = pathToThumbnailImage.split(".")[-1]
            thumbnailIm = PIL.Image.open(pathToThumbnailImage)
            item["thumbnailXsize"] = thumbnailIm.size[0]
            item["thumbnailYsize"] = thumbnailIm.size[1]
            item["thumbnailValue"] = base64.b64encode(open(pathToThumbnailImage, 'rb').read()).decode("utf-8")
        return item

    def addImage(self, pathToImage, imageTitle="", pathToThumbnailImage=None, thumbnailHeight=None, thumbnailWidth=None):
        if self.imageList is None:
            self.dictReport["items"].append(self.__createImageItem(pathToImage, imageTitle,
                                                                   pathToThumbnailImage, thumbnailHeight, thumbnailWidth))
        else:
            self.imageList["items"].append(self.__createImageItem(pathToImage, imageTitle,
                                                                  pathToThumbnailImage, thumbnailHeight, thumbnailWidth))

    def addTable(self, title, columns, data, orientation="horizontal"):
        item = {}
        item["type"] = "table"
        item["title"] = title
        item["columns"] = columns
        item["data"] = data
        item["orientation"] = orientation
        self.dictReport["items"].append(item)


    def addLogFile(self, title, linkText, pathToLogFile):
        item = {}
        item["type"] = "logFile"
        item["title"] = title
        item["linkText"] = linkText
        item["logText"] = unicode(open(pathToLogFile).read(), errors='ignore')
        self.dictReport["items"].append(item)


    def getDictReport(self):
        return self.dictReport


    def renderJson(self, pathToJsonDir):
        pathToJsonFile = os.path.join(pathToJsonDir, "report.json")
        open(pathToJsonFile, "w").write(json.dumps(self.dictReport, indent=4))
        return pathToJsonFile

    def escapeCharacters(self, strValue):
        strValue = html.escape(strValue)
        strValue = strValue.replace(unicode("Å"), "&Aring;")
        strValue = strValue.replace(unicode("°"), "&deg;")
        strValue = strValue.replace("\n", "<br>")
        return strValue


    # def renderHtml(self, pathToHtmlDir, nameOfIndexFile="index.html"):
    #     page = markupv1_10.page(mode='loose_html')
    #     page.init(title=self.dictReport["title"],
    #                     footer="Generated on %s" % time.asctime())
    #     page.div(align_="LEFT")
    #     page.h1()
    #     page.strong(self.dictReport["title"])
    #     page.h1.close()
    #     page.div.close()
    #     for item in self.dictReport["items"]:
    #         if "value" in item:
    #             itemValue = item["value"]
    #         if "title" in item:
    #             itemTitle = self.escapeCharacters(item["title"])
    #         if item["type"] == "info":
    #             page.p(itemValue)
    #         if item["type"] == "warning":
    #             page.font(_color="red", size="+1")
    #             page.p()
    #             page.strong(itemValue)
    #             page.p.close()
    #             page.font.close()
    #         elif item["type"] == "image":
    #             self.__renderImage(page, item, pathToHtmlDir)
    #             page.br()
    #             page.p(itemTitle)
    #         elif item["type"] == "images":
    #             page.table()
    #             page.tr(align_="CENTER")
    #             for item in item["items"]:
    #                 itemTitle = self.escapeCharacters(item["title"])
    #                 page.td()
    #                 page.table()
    #                 page.tr()
    #                 page.td()
    #                 self.__renderImage(page, item, pathToHtmlDir)
    #                 page.td.close()
    #                 page.tr.close()
    #                 page.tr(align_="CENTER")
    #                 page.td(itemTitle)
    #                 page.tr.close()
    #                 page.table.close()
    #                 page.td.close()
    #             page.tr.close()
    #             page.table.close()
    #             page.br()
    #         elif item["type"] == "table":
    #             titleBgColour = "#99c2ff"
    #             columnTitleBgColour = "#ffffff"
    #             dataBgColour = "#e6f0ff"
    #             page.table(border_="1",
    #                        cellpadding_="2",
    #                        width="100%",
    #                        style_="border: 1px solid black; border-collapse: collapse; margin: 0px; font-size: 12px")
    #             page.tr(align_="LEFT")
    #             # page.strong(itemTitle)
    #             page.th(itemTitle, bgcolor_=titleBgColour, align_="LEFT", style_="border: 1px solid black; border-collapse: collapse; padding: 5px;", colspan_=str(len(item["columns"])))
    #             page.tr.close()
    #             if "orientation" in item and item["orientation"] == "vertical":
    #                 for index1 in range(len(item["columns"])):
    #                     itemColumn = self.escapeCharacters(item["columns"][index1])
    #                     page.tr(align_="LEFT")
    #                     page.th(itemColumn, bgcolor_=columnTitleBgColour, align_="LEFT", style_="border: 1px solid black; border-collapse: collapse; padding: 5px;")
    #                     for index2 in range(len(item["data"])):
    #                         itemData = self.escapeCharacters(str(item["data"][index2][index1]))
    #                         page.th(itemData, bgcolor_=dataBgColour, style_="padding: 5px;")
    #                     page.tr.close()
    #             else:
    #                 page.tr(align_="LEFT", bgcolor_=columnTitleBgColour, style_="border: 1px solid black; border-collapse: collapse; padding: 5px;")
    #                 for column in item["columns"]:
    #                     itemColumn = self.escapeCharacters(column)
    #                     page.th(itemColumn, style_="border: 1px solid black; border-collapse: collapse; padding: 5px;")
    #                 page.tr.close()
    #                 for listRow in item["data"]:
    #                     page.tr(align_="LEFT", bgcolor_=dataBgColour, style_="border-collapse: collapse; padding: 5px;")
    #                     for cell in listRow:
    #                         itemCell = self.escapeCharacters(str(cell))
    #                         page.th(itemCell, style_="border: 1px solid black; border-collapse: collapse; padding: 5px;")
    #                     page.tr.close()
    #             page.table.close()
    #             page.br()
    #         elif item["type"] == "logFile":
    #             pathToLogHtml = os.path.join(pathToHtmlDir, itemTitle + ".html")
    #             if os.path.exists(pathToLogHtml):
    #                 fd, pathToLogHtml = tempfile.mkstemp(suffix=".html",
    #                                                      prefix=itemTitle.replace(" ", "_") + "_",
    #                                                      dir=pathToHtmlDir)
    #                 os.close(fd)
    #             pageLogHtml = markupv1_10.page()
    #             pageLogHtml.h1(itemTitle)
    #             pageLogHtml.pre(html.escape(item["logText"]))
    #             open(pathToLogHtml, "w").write(str(pageLogHtml))
    #             os.chmod(pathToLogHtml, 0o644)
    #             page.p()
    #             page.a(item["linkText"], href_=os.path.basename(pathToLogHtml))
    #             page.p.close()
    #     html = str(page)
    #     pagePath = os.path.join(pathToHtmlDir, nameOfIndexFile)
    #     filePage = open(pagePath, "w")
    #     filePage.write(html)
    #     filePage.close()
    #     return pagePath

    def __renderImage(self, page, item, pathToHtmlDir):
        imageName = item["title"].replace(" ", "_")
        pathToImage = os.path.join(pathToHtmlDir, "{0}.{1}".format(imageName, item["suffix"]))
        if os.path.exists(pathToImage):
            fd, pathToImage = tempfile.mkstemp(suffix="." + item["suffix"],
                                               prefix=imageName + "_",
                                               dir=pathToHtmlDir)
            os.close(fd)
        open(pathToImage, "wb").write(base64.b64decode(item["value"]))
        os.chmod(pathToImage, 0o644)
        if "thumbnailValue" in item:
            thumbnailImageName = imageName + "_thumbnail"
            pathToThumbnailImage = os.path.join(pathToHtmlDir, "{0}.{1}".format(thumbnailImageName, item["suffix"]))
            if os.path.exists(pathToThumbnailImage):
                fd, pathToThumbnailImage = tempfile.mkstemp(suffix="." + item["suffix"],
                                                            prefix=thumbnailImageName + "_",
                                                            dir=pathToHtmlDir)
                os.close(fd)
            open(pathToThumbnailImage, "wb").write(base64.b64decode(item["thumbnailValue"]))
            os.chmod(pathToThumbnailImage, 0o644)
            pageReferenceImage = markupv1_10.page(mode='loose_html')
            pageReferenceImage.init(title=imageName, footer="Generated on %s" % time.asctime())
            pageReferenceImage.h1(imageName)
            pageReferenceImage.br()
            pageReferenceImage.img(src=os.path.basename(pathToImage),
                                   title=imageName,
                                   width=item["xsize"], height=item["ysize"])
            pageReferenceImage.br()
            pathPageReferenceImage = os.path.join(pathToHtmlDir, "{0}.html".format(imageName))
            filePage = open(pathPageReferenceImage, "w")
            filePage.write(str(pageReferenceImage))
            filePage.close()
            page.a(href=os.path.basename(pathPageReferenceImage))
            page.img(src=os.path.basename(pathToThumbnailImage),
                     title=imageName, width=item["thumbnailXsize"], height=item["thumbnailYsize"])
            page.a.close()
        else:
            page.img(src=os.path.basename(pathToImage),
                     title=item["title"],
                     width=item["xsize"],
                     height=item["ysize"])

