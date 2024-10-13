import instrument as ins
'''Example for the operating condition below: 
1MHz, 3V square pulse 
-2V DC bias'''

scope = ins.scope_connection()
func_gen = ins.func_gen_connection()
k2400 = ins.source_conncetion()

ins.func_gen_setting(func_gen, 1E6, 3, 0) 
ins.func_gen_output(func_gen) 
ins.source_bias(k2400, -2) 
ins.scope_setting(scope, 1E5, 5, 0) 

time.sleep(0.5)
data1 = ins.scope_ascii_measure(scope)
time.sleep(0.05)
data2 = ins.scope_ascii_measure(scope)
time.sleep(0.05)
data3 = ins.scope_ascii_measure(scope)
time.sleep(0.05)
data4 = ins.scope_ascii_measure(scope)
time.sleep(0.05)
data5 = ins.scope_ascii_measure(scope)
x = (data1[0] + data2[0] + data3[0] + data4[0] + data5[0]) / 5
# EL intensity: y1 (y1 need inverse)
y1 = (data1[1] + data2[1] + data3[1] + data4[1] + data5[1]) / 5
y2 = (data1[2] + data2[2] + data3[2] + data4[2] + data5[2]) / 5
xinc = x[1] - x[0]
data = [x, -y1, y2, xinc]



