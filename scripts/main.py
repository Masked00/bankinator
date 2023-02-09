import cv2
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from imports import *
from preprocess import correct_line, strt_stp_pos_image, detect_horizontal_line
from extract_date import ext_date
from extract_amount import ext_amount
from extract_ocr_details import ext_ocr_details
from extract_MICR import extract_micr


def choose_file():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename()
    return file_path


def process_cheque(file_path):
    img_color = cv2.imread(file_path)
    if img_color.ndim == 3:
        img = cv2.cvtColor(img_color, cv2.COLOR_RGB2GRAY)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU)[1]
    cv2.imwrite('img_th.jpg', img)

    line_corrected_img, mask = correct_line(img)
    cv2.imwrite('preprocessed_img.jpg', line_corrected_img)

    extracted_micr = extract_micr(image=line_corrected_img)[0]

    date = ext_date(line_corrected_img, mask)
    template = cv2.imread('./rupee_template_2.jpg', 0)
    amount = ext_amount(line_corrected_img, template)

    details = ext_ocr_details(line_corrected_img)
    detail = details[:-1]
    signature = details[-1]
    fields = ['PayeeName', 'AC/NO', 'IFSC']
    cheque_fields = {}
    for field, checK_field in zip(fields, detail):
        cheque_fields.update({field: checK_field})
    cheque_fields.update({'Amount': amount})
    cheque_fields.update({'Cheque MICR Number': extracted_micr})

    details_df = pd.DataFrame(cheque_fields, index=[0])
    details_df['Signature'] = pd.Series(index=details_df.index)

    writer = pd.ExcelWriter('./Cheque_details.xlsx', engine='xlsxwriter')
    details_df.to_excel(writer, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    worksheet.insert_image('G2', './fields/signature.jpg')

    writer.save()


if __name__ == "__main__":
    file_path = choose_file()
    process_cheque(file_path)
