import sys, os, time
import win32com.client
src = os.path.abspath(sys.argv[1]); dst = os.path.abspath(sys.argv[2])
app = win32com.client.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(src, ReadOnly=True, Untitled=False, WithWindow=False)
pres.SaveAs(dst, 32)   # 32 = ppSaveAsPDF
pres.Close(); app.Quit()
print("exported", dst, os.path.getsize(dst) // 1024, "KB")
