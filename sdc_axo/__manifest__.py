# -*- coding: utf-8 -*-

{
    'name': 'Axo Top Media',
    'version': '1.0',
    'author': 'Ait-Mlouk Addi',
    'website': 'https://www.sdatacave.com',
    'support': 'aitmlouk@gmail.com',
    'license': "AGPL-3",
    'complexity': 'easy',
    'sequence': 1,
    'category': 'sale',
    'description': """
        Put your description here for your module:
            - model1
            - model2
            - model3
    """,
    'depends': ['base','mail','sale','account'],
    'summary': 'sale, purchase',
    'data': [
        'views/axo_views.xml',
        'views/axo_inherit.xml',
        'data/sequence.xml',
        'report/sale_report.xml',
        'report/report.xml',
        'report/sale_report_print_comm.xml',
        'report/sale_report_print.xml',
        'report/report_invoice.xml',
        'menu.xml',
    ],
    
    'css': [
        #'static/src/css/ModuleName_style.css'
    ],
    
    'installable': True,
    'application': True,
}
