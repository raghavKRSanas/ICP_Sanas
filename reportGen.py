import matplotlib.pyplot as plt
import numpy as np
from jinja2 import Template

# Example data and comments
# data1 = {'Creative_hs220_Female_IN-Hindi_1716798660408': 0.1767810026385224, 'EnterGo_analysis_410_8x8_Female_IN-Hindi_1716545609879': 0.1965811965811966, 'FRONTECH_HEADSET_H_3447_Female_IN-Hindi_1716797580787': 0.2792553191489361, 'InplayHN620_analysis_410_8x8_Female_IN-Hindi_1716550570705': 0.1280653950953679, 'JabraBiz1100_analysis_410_8x8_Female_IN-Hindi_1716544040775': 0.1575, 'Jabra_Biz_2300_410_8x8__Female_IN-Hindi_1716812638660': 0.08353808353808354, 'Lenovo_USB_analysis_410_8X8_Female_IN-Hindi_1716798411115': 0.1393034825870647, 'Logitech_H570e_analysis_410_8X8_Female_IN-Hindi_1716798705932': 0.1802884615384615, 'Mairdi_analysis_410_8x8_Female_IN-Hindi_1716550038582': 0.1533333333333333}
# data2 = {'Creative_hs220_Female_IN-Hindi_1716798660408': 0.1424802110817942, 'EnterGo_analysis_410_8x8_Female_IN-Hindi_1716545609879': 0.207977207977208, 'FRONTECH_HEADSET_H_3447_Female_IN-Hindi_1716797580787': 0.25, 'InplayHN620_analysis_410_8x8_Female_IN-Hindi_1716550570705': 0.1362397820163488, 'JabraBiz1100_analysis_410_8x8_Female_IN-Hindi_1716544040775': 0.145, 'Jabra_Biz_2300_410_8x8__Female_IN-Hindi_1716812638660': 0.07862407862407862, 'Lenovo_USB_analysis_410_8X8_Female_IN-Hindi_1716798411115': 0.1318407960199005, 'Logitech_H570e_analysis_410_8X8_Female_IN-Hindi_1716798705932': 0.1514423076923077, 'Mairdi_analysis_410_8x8_Female_IN-Hindi_1716550038582': 0.12}
# comments = {'Creative_hs220_Female_IN-Hindi_1716798660408': 'WER is more in model: 1.24.0619.2 app version 0.24.0619.6 by 0.03 when compared to model: 1.24.0410.1 appversion: 2.24.0513.4', 'EnterGo_analysis_410_8x8_Female_IN-Hindi_1716545609879': 'WER is more in model: 1.24.0410.1 app version 2.24.0513.4 by 0.01 when compared to model: 1.24.0619.2 appversion: 0.24.0619.6', 'FRONTECH_HEADSET_H_3447_Female_IN-Hindi_1716797580787': 'WER is more in model: 1.24.0619.2 app version 0.24.0619.6 by 0.03 when compared to model: 1.24.0410.1 appversion: 2.24.0513.4', 'InplayHN620_analysis_410_8x8_Female_IN-Hindi_1716550570705': 'WER is more in model: 1.24.0410.1 app version 2.24.0513.4 by 0.01 when compared to model: 1.24.0619.2 appversion: 0.24.0619.6', 'JabraBiz1100_analysis_410_8x8_Female_IN-Hindi_1716544040775': 'WER is more in model: 1.24.0619.2 app version 0.24.0619.6 by 0.01 when compared to model: 1.24.0410.1 appversion: 2.24.0513.4', 'Jabra_Biz_2300_410_8x8__Female_IN-Hindi_1716812638660': 'WER is more in model: 1.24.0619.2 app version 0.24.0619.6 by 0.00 when compared to model: 1.24.0410.1 appversion: 2.24.0513.4', 'Lenovo_USB_analysis_410_8X8_Female_IN-Hindi_1716798411115': 'WER is more in model: 1.24.0619.2 app version 0.24.0619.6 by 0.01 when compared to model: 1.24.0410.1 appversion: 2.24.0513.4', 'Logitech_H570e_analysis_410_8X8_Female_IN-Hindi_1716798705932': 'WER is more in model: 1.24.0619.2 app version 0.24.0619.6 by 0.03 when compared to model: 1.24.0410.1 appversion: 2.24.0513.4', 'Mairdi_analysis_410_8x8_Female_IN-Hindi_1716550038582': 'WER is more in model: 1.24.0619.2 app version 0.24.0619.6 by 0.03 when compared to model: 1.24.0410.1 appversion: 2.24.0513.4'}


# Function to generate an HTML report with Bootstrap, Chart.js, and comments
def generate_html_report_with_comments(data1, data2, comments, model1, model2, bestModel):
    keys = list(data1.keys())
    values1 = [data1[key] for key in keys]
    values2 = [data2.get(key, 0) for key in keys]

    # Generate the bar chart
    ind = np.arange(len(keys))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(ind - width/2, values1, width, label=f'{model1}', color='skyblue')
    rects2 = ax.bar(ind + width/2, values2, width, label=f'{model2}', color='orange')

    ax.set_xlabel('Keys')
    ax.set_ylabel('Values')
    ax.set_title(f'Comparison of {model1} and {model2}')
    ax.set_xticks(ind)
    ax.set_xticklabels(keys, rotation=45, ha='right')
    ax.legend()

    # Save the bar chart to a file
    chart_filename = 'comparison_chart.png'
    plt.savefig(chart_filename)

    # Prepare data for JavaScript chart (Chart.js)
    data_str = str(values1)
    data2_str = str(values2)
    labels_str = str(keys)

    # Read HTML template
    with open('templateUpdated.html', 'r') as file:
        template_str = file.read()

    # Create Jinja2 template object
    template = Template(template_str)

    # Render HTML using template and data
    report_html = template.render(
        chart_filename=chart_filename,
        data_str=data_str,
        data2_str=data2_str,
        labels_str=labels_str,
        data1=data1,
        data2=data2,
        comments=comments,
        bestModel=bestModel,
        model2=model2,
        model1=model1
    )

    return report_html



def main(data1, data2, comments, model1, model2, bestModel):
    # Generate the report with comments
    report_content = generate_html_report_with_comments(data1, data2, comments, model1, model2, bestModel)
    # Save the report to a file
    report_filename = 'comparison_report_with_comments.html'
    with open(report_filename, 'w') as f:
        f.write(report_content)
    print(f"Report generated successfully: {report_filename}")


