# -*- coding: utf-8 -*-

from duplicateDetector.pairholder import PairHolder

# TODO: Research robert cecil martin – clean code
# TODO: Recherchieren wie man wort bedeutung unterscheiden kann
# TODO: Fix keep in create graph


def run(excel_sheet_path):
    holder = PairHolder.get_holder_from_excel(excel_sheet_path)
    result = holder.run_levenshtein(1, ["NAME1"], "NAME1", data_limit=500)
    result2 = holder.run_jaro_winkler(0.15, ["NAME1", "STRAS"], "NAME1", data_limit=500)
    result3 = holder.run_cosine(0.9, ["NAME1", "STRAS", "ORT01", "PSTLZ", "LAND1"], "_KNA1.KUNNR", data_limit=None)
    print(result.shape)
    print(result2.shape)
    print(result3.shape)


def run_same_countries(excel_sheet_path, result_path, precision):
    holder = PairHolder.get_holder_from_excel(excel_sheet_path)
    countries = holder.get_unique_column_values("LAND1")
    for country in countries:
        countries_result = holder.run_cosine(precision, ["NAME1", "STRAS"], "NAME1", data_limit=None,
                                             filter_field="LAND1", filter_value=country)
        holder.save_to_csv(countries_result, result_path+country+".csv")
    return True


def run_all_countries(excel_sheet_path, result_path):
    holder = PairHolder.get_holder_from_excel(excel_sheet_path)
    result = holder.run_cosine(0.8, ["NAME1", "STRAS", "ORT01", "PSTLZ", "LAND1"], "_KNA1.KUNNR", data_limit=None)
    holder.save_to_csv(result, result_path)


def cluster_cosine(excel_sheet_path):
    holder = PairHolder.get_holder_from_excel(excel_sheet_path)
    result = holder.cluster_cosine(0.8, ["NAME1", "STRAS", "ORT01"], "NAME1", filter_field="LAND1", filter_value="DE")
    print(result)


def run_filter_cluster(excel_sheet_path):
    holder = PairHolder.get_holder_from_excel(excel_sheet_path)
    result = holder.run_cluster(0.8, ["NAME1", "STRAS"], "NAME1", data_limit=None,
                                min_cluster_size=3, filter_field="LAND1", filter_value="DE", plot=True)
    print(result)


def plot_cosine_de(excel_sheet_path):
    holder = PairHolder.get_holder_from_excel(excel_sheet_path)
    holder.plot_cosine(0.8, ["NAME1", "STRAS", "ORT01"], "NAME1", filter_field="LAND1", filter_value="DE")


if __name__ == "__main__":
    sheet_path = "/Users/Moritz/Downloads/Customers.xlsx"
    # run("/Users/Moritz/Downloads/Chinese_Customers.xlsx")
    # run_same_countries("/Users/Moritz/Downloads/Customers.xlsx", "/Users/Moritz/Desktop/customer_results_05.csv", 0.5)
    # run_same_countries("/Users/Moritz/Downloads/Customers.xlsx", "/Users/Moritz/Desktop/customer_results_06.csv", 0.6)
    # run_same_countries("/Users/Moritz/Downloads/Customers.xlsx", "/Users/Moritz/Desktop/customer_results_09.csv", 0.9)
    # run_all_countries("/Users/Moritz/Downloads/Customers.xlsx", "/Users/Moritz/Desktop/customer_results.csv")
    # run_cluster("/Users/Moritz/Documents/Customers_DE.xlsx")
    # run_filter_cluster(sheet_path)
    # cluster_cosine(sheet_path)
    plot_cosine_de(sheet_path)



