{
    "name": "Letter of Credit Management",
    "version": "1.0",
    "category": "Accounting",
    "summary": "Manage Letters of Credit (LCs) linked with Purchase Orders and Bills",
    "description": "Full LC workflow: tracking, accounting, linking to POs and bills.",
    "author": "Khondokar Md. Mehedi Hasan",
    "depends": ["purchase", "stock", "account", "stock_landed_costs"],
    "data": [
        # data
        "data/ir_sequence.xml",
        "security/ir.model.access.csv",
        # view
        "views/lc_management_views.xml",
        "views/lc_type_views.xml",
        "views/account_move_view.xml",
        "views/purchase_order_view.xml",
        "views/landed_cost_view.xml",
        "views/stock_picking_view.xml",
        "views/menu.xml"

    ],
    "installable": True,
    "application": True,
    'license': 'LGPL-3',
}