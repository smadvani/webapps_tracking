# -*- coding: utf-8 -*-
"""
project_tracking.py

Created on Tue Nov 22 11:59:53 2016

@author: sadvani
PURPOSE: For tracking funds and hourly development for web apps projects
H:\01_ISB\PlanningTools>pyuic4 ui_project_track.ui -o ui_project_track.py
"""
import sys
import ui_project_track as ui
from PyQt4 import QtCore, QtGui
import sqlite3 

#form_class = uic.loadUiType("tempconv.ui")[0]                 # Load the UI
 
class MyDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = ui.Ui_Dialog()
        self.ui.setupUi(self)
        dbstr = QtGui.QFileDialog.getOpenFileName(None, 'Open Database File', 'C:\\')
        #print dbstr
        #print self.ui.tabMain.currentIndex()
        self.populate_cbx(dbstr)
        self.ui.pbCalcDev.clicked.connect(self.calc_available)
        self.ui.pbPostNewProj.clicked.connect(lambda: self.post_calcs(dbstr))
        self.ui.tabMain.currentChanged.connect(lambda: self.review_projects(dbstr))
        self.ui.rbFundsTrnsfrd.clicked.connect(self.enable_TO)
        self.ui.pbClose.clicked.connect(self.close_app)
    
    def enable_TO(self):
        if self.ui.rbFundsTrnsfrd.isChecked():
            self.ui.txtTO.setEnabled(True)
            self.ui.lblTO.setEnabled(True)
            self.ui.txtTO.setFocus()
        else:
            self.ui.txtTO.setEnabled(False)
            self.ui.lblTO.setEnabled(False)
        
    def populate_cbx(self, dbstr):
        #print dbstr
        con = sqlite3.connect(str(dbstr))
        cur = con.cursor()
        cur.execute("select last_name||', '||first_name from personnel where role = 'PI' order by last_name, first_name;")
        pi_list = cur.fetchall()
        self.ui.cbxPI.addItem("Select PI")
        for pi_ in pi_list:
            self.ui.cbxPI.addItem(pi_[0])
        cur.execute("select last_name||', '||first_name from personnel where role = 'PM' order by last_name, first_name;")
        pm_list = cur.fetchall()
        self.ui.cbxPM.addItem("Select PM")
        for pm_ in pm_list:
            self.ui.cbxPM.addItem(pm_[0])
        cur.execute("select agency_code from agency order by agency_code;")
        sponsors = cur.fetchall()
        self.ui.cbxSponsor.addItem("Select Sponsor")
        for spon in sponsors:
            self.ui.cbxSponsor.addItem(spon[0])
        con.close()
        
    def calc_available(self):
        if self.ui.sbxBudgetGross.value() == 0.00:
            QtGui.QMessageBox.warning(None,'Missing value', 'Set Gross Funding number') 
            self.ui.sbxBudgetGross.setFocus()
        #! Assumed hourly set with a default value
        #elif self.ui.sbxHrlyrate.value() == 0.00:
            #QtGui.QMessageBox.warning(None,'Missing value', 'Set Assumed Hourly Rate') 
            #self.ui.sbxHrlyrate.setFocus()
        elif self.ui.sbxFixedPM.value() == 0.00:
            PM = QtGui.QMessageBox.question(None, 'Fixed (PM) set to zero', "Add PM costs?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)            
            #QtGui.QMessageBox.warning(None,'Missing value', 'Set Overhead Rate') 
            if  PM == QtGui.QMessageBox.Yes:            
                self.ui.sbxFixedFed.setFocus()
            else:
                QtGui.QMessageBox.warning(None,'Zero value', 'PM Rate Set at Zero') 
        elif self.ui.sbxFixedSys.value() == 0.00:
            Sys = QtGui.QMessageBox.question(None, 'Fixed (Systems) set to zero', "Add Systems costs?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)            
            #QtGui.QMessageBox.warning(None,'Missing value', 'Set Overhead Rate') 
            if  Sys == QtGui.QMessageBox.Yes:            
                self.ui.sbxFixedFed.setFocus()
            else:
                QtGui.QMessageBox.warning(None,'Zero value', 'Systems Rate Set at Zero') 
        elif self.ui.sbxOH.value() == 0.00:
            OHzero = QtGui.QMessageBox.question(None, 'Overhead set to zero', "Add overhead?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)            
            #QtGui.QMessageBox.warning(None,'Missing value', 'Set Overhead Rate') 
            if  OHzero == QtGui.QMessageBox.Yes:            
                self.ui.sbxOH.setFocus()
            else:
                QtGui.QMessageBox.warning(None,'Zero Value', 'Overhead Rate Set at Zero') 
        #! Calcu
        
        net_funds = self.ui.sbxBudgetGross.value() - (self.ui.sbxBudgetGross.value() * self.ui.sbxOH.value()/100.0)
        
        if self.ui.rbFEDpct.isChecked():
            fed = (self.ui.sbxFed.value()/100.0) * net_funds
        else:
            fed = self.ui.sbxFed.value()/100.0
        if self.ui.rbPMpct.isChecked():
            pm = (self.ui.sbxFixedPM.value()/100.0) * net_funds
        else:
            pm = self.ui.sbxFixedPM.value()
        if self.ui.rbSYSpct.isChecked():
            sys = (self.ui.sbxFixedSys.value()/100.0) * net_funds
        else:
            sys = self.ui.sbxFixedSys.value()
        hosting = self.ui.sbxHosting.value()
        #! set all percetages based on gross
        dev_funds = (net_funds - (fed + pm + sys + hosting))
        dev_hrs = dev_funds/self.ui.sbxHrlyrate.value()
        self.ui.txtNetFunds.setText(str(net_funds))        
        self.ui.txtDevFunding.setText(str(dev_funds))
        self.ui.txtDevHrs.setText(str(dev_hrs))
        
    def post_calcs(self, dbstr):
        self.calc_available()
        pi = self.ui.cbxPI.currentText()
        pi_lst_nm = pi.split(",")[0]
        pi_fst_nm = pi.split(",")[1]
        pm = self.ui.cbxPM.currentText()
        pm_lst_nm = pm.split(",")[0]
        pm_fst_nm = pm.split(",")[1]
        con = sqlite3.connect(str(dbstr))
        cur = con.cursor()
        #print "select personnel_id from personnel where last_name = '"+ pi_lst_nm.strip() +"' and first_name = '"+ pi_fst_nm.strip() +"';)"
        cur.execute("select personnel_id from personnel where last_name = '"+ pi_lst_nm.strip() +"' and first_name = '"+ pi_fst_nm.strip() +"';")
        pi_id = cur.fetchone()[0]
        
        cur = con.cursor()
        #print "select personnel_id from personnel where last_name = '"+ pm_lst_nm.strip() +"' and first_name = '"+ pm_fst_nm.strip() +"';)"
        cur.execute("select personnel_id from personnel where last_name = '"+ pm_lst_nm.strip() +"' and first_name = '"+ pm_fst_nm.strip() +"';")
        pm_id = cur.fetchone()[0]
        
        
        strt_yr = int(self.ui.sbxYear.value())
        fisc_yr = int(self.ui.sbxFiscalYear.value())
        if self.ui.rbFundsTrnsfrd.isChecked():
            fnd_trnsfrd = 1
        else:
            fnd_trnsfrd = 0
        msg = ''
        try:   
            insrt_proj = "insert into project (project_code, project_full_name, primary_inves, pm, start_year, funds_transferred) " \
                "values ('" +self.ui.txtPrjCode.toPlainText() +"', '"+ self.ui.txtProject.toPlainText()  +"', "+  str(pi_id) +", " \
                + str(pm_id) +", "+ str(strt_yr) +", "+ str(fnd_trnsfrd) +");"
    #        QtGui.QMessageBox.warning(None,'insert', str(insrt_proj))
            cur = con.cursor()
            cur.execute(insrt_proj)
            con.commit()
            msg = 'Project'
        except Exception as e: #print('Error inserting new project: ' + e)
            QtGui.QMessageBox.warning(None, 'Error inserting new project', str(e))
        try:            
            insrt_plan = "insert into project_plan (project_code,task_order, fiscal_year, agency_code, gross_funds, overhead_rate, fixed_pm_rate, fixed_sys_rate,  fed_rate, hosting, " \
                "avail_for_dev, assumed_dev_hrly, planned_hrs, assumptions) " \
                "values ('" +self.ui.txtPrjCode.toPlainText() +"', '"+ self.ui.txtTO.text() +"', "+  str(fisc_yr)  +", '"+  self.ui.cbxSponsor.currentText() +"', "+ str(self.ui.sbxBudgetGross.value()) +", " \
                + str(self.ui.sbxOH.value()) +", "+  str(self.ui.sbxFixedPM.value()) +", "+ str(self.ui.sbxFixedSys.value()) +", "+ str(self.ui.sbxFed.value()) +", "+ str(self.ui.sbxHosting.value()) +", " \
                + str(round(float(self.ui.txtDevFunding.toPlainText()),2)) +", "+ str(round(float(self.ui.sbxHrlyrate.value()),2)) +", "+ str(round(float(self.ui.txtDevHrs.toPlainText()),0)) +", '"+ self.ui.txtAssumptions.toPlainText() +"');" 
    #        QtGui.QMessageBox.warning(None,'insert', str(insrt_plan))
            cur = con.cursor()
            cur.execute(insrt_plan)
            con.commit()
            if len(msg) == 0:
                msg = 'Budget planning numbers'
            else:
                msg = msg + ' and budget planning numbers'
            QtGui.QMessageBox.warning(None,'Data inserted', '%s inserted into the database'%(msg)) 
        except Exception as e: #print(e)
            QtGui.QMessageBox.warning(None, 'Error inserting new budget', str(e))
        
        
    def review_projects(self, dbstr):
        if self.ui.tabMain.currentIndex() == 1:
            con = sqlite3.connect(str(dbstr))
            cur = con.cursor()
            sel_revProj = "select pln.agency_code, prj.project_code,pln.task_order, per.last_name||', '||per.first_name, case when prj.funds_transferred = 0 then 'yes' else 'no' end as funded, pln.planned_hrs, " \
                "vw.jan, vw.feb, vw.mar, vw.apr, vw.may, vw.jun, vw.jul, vw.aug, vw.sep, vw.oct, vw.nov, vw.dec, vw.yr_tot, pln.planned_hrs-vw.yr_tot " \
                "from personnel as per inner join project as prj on prj.primary_inves = per.personnel_id inner join project_plan as pln on pln.project_code = prj.project_code " \
                "left outer join vw_hrs_rpt as vw on vw.project_code = pln.project_code and vw.fiscal_year = pln.fiscal_year and vw.agency_code = pln.agency_code and vw.task_order = pln.task_order " \
                "order by pln.agency_code, prj.project_code, pln.planned_hrs; "
            #print sel_revProj
            cur.execute(sel_revProj)
            prj = cur.fetchall()
            for i, row in enumerate(prj):
                for j, val in enumerate(row):
                     self.ui.tblReviewProj.setItem(i,j,QtGui.QTableWidgetItem(str(val)))
            con.close()
            
    def close_app(self):
        QtGui.QApplication.quit()
        
if __name__ == "__main__":
        app = QtGui.QApplication(sys.argv)
        myapp = MyDialog()
        myapp.show()
        sys.exit(app.exec_())