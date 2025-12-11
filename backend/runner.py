from main import nse_lib_bhav, swing_screener, additions, addition_del_spike

def run_all_scripts():
    print("Running full pipeline...")
    print("fetching nse bhav data...")
    nse_lib_bhav.main()
    print("running swing screener...")
    swing_screener.main()
    additions.main()
    addition_del_spike.main()
    print("Pipeline complete!")

def run_weekly_setup():
    print("Running weekly setup...")
    import main.swing_weekly_setup
    main.swing_weekly_setup.main()
    print("Weekly setup complete!")