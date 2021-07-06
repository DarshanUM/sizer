# from reportlab.platypus import SimpleDocTemplate,BaseDocTemplate,\
#  Table, TableStyle, Paragraph,Spacer, PageBreak, KeepTogether
# from reportlab.lib.styles import *
# from reportlab.lib.pagesizes import A4
# from reportlab.lib.units import inch,mm
# from reportlab.lib import colors
# from reportlab.lib.enums import TA_LEFT, TA_CENTER,TA_JUSTIFY,TA_RIGHT
# import os
# from reportlab.graphics.shapes import Drawing
# from reportlab.graphics.widgets.markers import makeMarker
# from reportlab.graphics.charts.linecharts import HorizontalLineChart
# # from reportlab.graphics.charts.lineplots import LinePlot
# from PIL import Image
# from reportlab.graphics.charts.legends import Legend
#
# styles = getSampleStyleSheet()
# class TableForm(object):
#     def __init__(self,Elements):
#         self.ele = Elements
#
#     def style_table(self,val,dikey,type):
# 	pass
#
#     def style_table_der(self,val):
# 	pass
#
#     def workload(self,val):
#         style = TableStyle(
#                 [
#                 ('ALIGN',(1,1),(-1,-1),'RIGHT'),
#                 ('LINEBELOW', (0,0), (-1,len(val)), 0.5,\
#                   colors.black),
#                 ('FONTSIZE', (0,0),(-1,0),13),
#                 ('FONTSIZE', (0,1),(-1,-2),12),
#                 ('FONTSIZE', (0,-1),(-1,-1),13),
#                 ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
#                 ('VALIGN',(0,-1),(0,-1),'MIDDLE'),
#                 ('BOX', (0,0), (-1,len(val)), 0.25, \
#                  colors.black),
#                 ('BACKGROUND', (0,0), (-1,0), \
#                  '#A3A3A3')
#                 ]
#                           )
#         style.add('ALIGN', (1,1),(-1,-1),'RIGHT')
#         s = getSampleStyleSheet()
#         s = s["Normal"]
#         s.wordWrap = 'CJK'
#         data2 = [[Paragraph(cell, s) for cell in row] \
#                  for row in val]
#         t=Table(data2,colWidths= [inch,1.5*inch,3.5*inch])
#         t.setStyle(style)
#         self.ele.append(KeepTogether(t))
#         return self.ele
#
#     def pagebreak(self):
#         self.ele.append(PageBreak())
#         return self.ele
#
#     def title(self,item):
#         for key,val in item.items():
#             text = key+":"+"      " + str(val)
#             self.ele.append(Paragraph(text,\
#                                       styles["Heading2"]))
#             self.ele.append(Spacer(0,mm*5))
#         return self.ele
#
#     def append(self,text,font):
#         self.ele.append(Paragraph(text,styles[font]))
#         return self.ele
#
#
#     def addPageNumber(self,canvas, doc):
#         """
#         Add the page number
#         """
#         page_num = canvas.getPageNumber()
#         text = "Page #%s" % page_num
#         canvas.drawRightString(200*mm, 10*mm, text)
#         img = os.getcwd() + "/static/images/maple_logo2.png"
#         canvas.drawImage(img, 20, 780, width = 143, height = 58, preserveAspectRatio=True)
#
#     def outline(self):
#          Canvas.setFillColor(colors.red)
#          Canvas.rect(150,100,10,5, fill=True, stroke=False)
#          Canvas.setFillColor(colors.green)
#          Canvas.rect(150,85,10,5, fill=True, stroke=False)
#
#     def graphout(self,catnames, data, min, max, step, ven1, ven2):
#         """
#         """
#         drawing = Drawing(400, 200)
#         lc = HorizontalLineChart()
#         lc.x = 30
#         lc.y = 50
#         lc.height = 125
#         lc.width = 350
#         lc.data = data
#         lc.categoryAxis.labels.boxAnchor = 'ne'
#         lc.categoryAxis.labels.angle     = 45
#         lc.categoryAxis.categoryNames = catnames
#         lc.valueAxis.valueMin = min
#         lc.valueAxis.valueMax = max
#         lc.valueAxis.valueStep = step
#         lc.lines[0].symbol = makeMarker('FilledCircle') # added to make filled circles.
#         lc.lines[0].strokeColor = colors.green
#         lc.lines[1].strokeColor = colors.red
#         lc.lines[1].symbol = makeMarker('FilledDiamond')
#         lc.lines[1].strokeWidth = 1.5
#         drawing.add(lc)
#         lgnd_obj = Legend()
#         lgnd_obj.alignment = 'right'
#         lgnd_obj.x = 410
#         lgnd_obj.y = 160
#         lgnd_obj.deltax = 60
#         lgnd_obj.dxTextSpace = 10
#         lgnd_obj.columnMaximum = 4
#         items = [(colors.red, ven2), (colors.green, ven1)]
#         lgnd_obj.colorNamePairs = items
#         drawing.add(lgnd_obj, 'legend')
#
#         return drawing
#
#     def pdfFilePath(self,scenario_name):
#         path = os.getcwd() + "/PDF/"+ scenario_name + ".pdf"
#         pdf = SimpleDocTemplate(path, pagesize = A4)
# 	return path,pdf
