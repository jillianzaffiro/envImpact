import olca


# Start openLCA
# Open the Construction DB
#    Verify 'SimpleBridge' in Product systems
#    Verify 'EF 3.0 Method' in 'Indicators and parameters' --> Impact assessment methods
# Tools -> Developer tools "IPC Server"
#    Choose port 8088
#
class LCAConnectorMC:
    def __init__(self, logger):
        self._lgr = logger
        self.port = 8080

    def _set_up_client(self):
        # https://github.com/GreenDelta/olca-ipc.py
        client = olca.Client(self.port)
        setup = olca.CalculationSetup()

        # define the calculation type here
        # see http://greendelta.github.io/olca-schema/html/CalculationType.html
        setup.calculation_type = olca.CalculationType.MONTE_CARLO_SIMULATION
        return client, setup

    def _close(self, client, result):
        self._lgr.info("Close connection to LCA")
        # the result remains accessible (for exports etc.) until
        # you dispose it, which you should always do when you do
        # not need it anymore
        client.dispose(result)

    def get_co2(self, surface_area, concrete, steel):
        try:
            co2 = self._get_co2(surface_area, concrete, steel)
            return True, co2
        except Exception:
            return False, "Cannot connect to LCA system"

    def _get_co2(self, surface_area, concrete, steel):
        """
        :param surface_area: Size of bridge in square feet
        :return: CO2 emissions in KG
        """
        client, setup = self._set_up_client()

        # select the product system and LCIA method
        setup.impact_method = client.find(olca.ImpactMethod, 'EF 3.0 Method')
        setup.product_system = client.find(olca.ProductSystem, 'SimpleBridge')
        setup.product_system = client.find(olca.ProductSystem, 'Energy')

        # amount is the amount of the functional unit (fu) of the system that
        # should be used in the calculation; unit, flow property, etc. of the fu
        # can be also defined; by default openLCA will take the settings of the
        # reference flow of the product system
        setup.amount = surface_area

        setup.amount = concrete
        setup.amount = steel


        # create the simulator
        simulator = client.simulator(setup)

        # client.excel_export(result, 'result.xlsx')
        for i in range(0,10):
            result = client.next_simulation(simulator)
            first_impact = result.impact_results[0]
            print('iteration %i: result for %s = %4.4f' %
                  (i, first_impact.impact_category.name, first_impact.value))

        # client.excel_export(simulator, 'simulation_result.xlsx')

        # co2 = 0.0
        # for idx in range(len(result.impact_results)):
        #     cur_result = result.impact_results[idx]
        #     name = cur_result.impact_category.name
        #     units = cur_result.impact_category.ref_unit
        #     val = cur_result.value
        #     # print(f"{name}: {val} {units}")
        #     if "Climate change" == name and units == "kg CO2 eq":
        #         co2 += val
        #
        # self._lgr.info(f"CO2: {co2:.2f} kg")

        self._close(client, simulator)
        return simulator
        # return co2