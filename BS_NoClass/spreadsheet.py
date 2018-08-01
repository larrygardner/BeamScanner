def spreadsheet(time_data, pos_data, vvm_data, save_name):

    import os
    import pyoo
    
    # Creates localhost for libre office
    os.system("soffice --accept='socket,host=localhost,port=2002;urp;' --norestore --nologo --nodefault # --headless")
    # Uses pyoo to open spreadsheet
    desktop = pyoo.Desktop('localhost',2002)
    doc = desktop.create_spreadsheet()
    
    x_data = []
    y_data = []
    amp_data = []
    phase_data = []
    
    for i in range(len(pos_data)):
        x_data.append(pos_data[i][0])
        y_data.append(pos_data[i][1])
    
        if type(vvm_data[0]) == tuple:
            amp_data.append(vvm_data[i][0])
            phase_data.append(vvm_data[i][1])
        
        elif type(vvm_data[0]) == str:
            amp_data.append(float(vvm_data[i].split(",")[0]))
            phase_data.append(float(vvm_data[i].split(",")[1]))
    
    try:
        # Writes data to spreadsheet
        sheet = doc.sheets[0]
        sheet[0,0:5].values = ["Time (s)","X Position (mm)", "Y Position (mm)", "Amplitude (dB)", "Phase (deg)"]
        
        sheet[1:len(time_data)+1, 0].values = time_data
        sheet[1:len(pos_data)+1, 1].values = x_data
        sheet[1:len(pos_data)+1, 2].values = y_data
        sheet[1:len(pos_data)+1, 3].values = amp_data
        sheet[1:len(pos_data)+1, 4].values = phase_data

        doc.save('BeamScannerData/' + str(save_name) + '.xlsx')
        doc.close()

    except (ValueError, KeyboardInterrupt, RuntimeError):
        doc.close()
        pass

