import re

text = "20250207T155041_140893.WFE1_CONTACT_HISTORY.csv:35708|79236|2025020715504159667866943158070|66943158070|1329900479490262481|{}|PREPAID||SMS|OUTBOUND|OUTBOUND|OUTBOUND|OUTBOUND_NOTIFICATION|Application Usage|DNA_TOL|0|PP_INFO|DNA_TOL|08/03/2023 00:00:00|08/03/2033 00:00:00||INFO_TOL|15321:โอกาสพิเศษ! สำหรับลูกค้าดีเเทค รับส่วนลด 200 บาท/เดือน เมื่อสมัครโปรเน็ตบ้านไฟเบอร์ทรู 500Mbps เเถมเมชไวไฟ/กล้องCCTV เเละรับชมฟรีเเอปบันเทิงสุดปัง สนใจคลิก https://dtac.co.th/s/FMCTOL /โทร 027008080|TH|||SUCCESS|DNA_TOL|02/07/2025 15:50:41||0|DNA Wave 2 TOL (30)"
pattern = r'^[^:]+:(.*)'

match = re.match(pattern, text)
if match:
    result = match.group(1)
    print(result)