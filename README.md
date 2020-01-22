What are all these Qt blacklisted tests, anyway
===============================================

Usage:
    python blackadder.py /path/to/tests/auto [platform] [--runtests] [--blame]

This will search for BLACKLIST files, parse them, filter for a spesific platform,
and then optionally run the blacklisted test functions and git blame the BLACKLIST. 

A report appears:

    qmenu                         task258920_mouseBorder                                 ['BPASS']                     osx            1b4ce373 2015 Blacklist task258920_mouseBorder on Mac
    qmenu                         submenuTearOffDontClose                                ['PASS']                      osx-10.11 ci   3e67f727 2017 Ignore failure of tst_qmenu::submenuTearOffDon
    qmenu                         submenuTearOffDontClose                                ['PASS']                      osx-10.12 ci   3e67f727 2017 Ignore failure of tst_qmenu::submenuTearOffDon
    qmenu                         layoutDirection                                        ['PASS']                      osx ci         2e3e8cec 2017 macOS: Blacklist tst_QMenu::layoutDirection
    qmenu                         pushButtonPopulateOnAboutToShow                        ['BFAIL']                     osx            58685a48 2017 macOS: Blacklist tst_QMenu::pushButtonPopulate
    qmenu                         tearOff                                                ['BPASS']                     osx            593719aa 2017 macOS: Blacklist flakey test tst_QMenu::tearOf
    qcombobox                     task260974_menuItemRectangleForComboBoxPopup           ['PASS']                      osx-10.10      cf5e3f37 2015 Tests: Blacklist task260974_menuItemRectangleF
    qcombobox                     task_QTBUG_56693_itemFontFromModel                     ['BFAIL']                     osx            f948f96e 2017 macOS: Blacklist tst_QComboBox::task_QTBUG_566
    qtoolbutton                   task176137_autoRepeatOfAction                          ['PASS']                      osx ci         22aa919b 2017 macOS: Blacklist tst_QToolButton::task176137_a
    qmdiarea                      updateScrollBars                                       ['BFAIL']                     osx            00b1360d 2014 Blacklist constantly failing test cases on OS 

A summary is printed at the end, adding up the individual pass/fails,
thereby giving some needed justification for the program name.

    Totals: Pass   86 Fail   17 Unknown   18
    Rate  : Pass  71% Fail  14% Unknown  15%
