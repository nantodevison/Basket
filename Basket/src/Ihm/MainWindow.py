'''
Created on 14 mars 2021

@author: Martin
module de conversion des fichiers .ui en .py
'''

from PyQt5 import QtWidgets, uic


class WindowPrincipale(QtWidgets.QMainWindow):
    '''
    la fenetre contenant le QtTablWidget principal
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        super(WindowPrincipale, self).__init__()
        uic.loadUi('FenetreBaseStat-TTFL.ui', self)
        
if __name__=="__main__" : 
    import sys 
    app=QtWidgets.QApplication(sys.argv)
    window=WindowPrincipale()
    window.show()
    sys.exit(app.exec_())