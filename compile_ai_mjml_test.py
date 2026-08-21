import os
import re
import mrml

raw_mjml_body = """
<!-- Main Hero Banner -->
<mj-section background-color="#ffffff" padding="0px 20px 15px 20px">
  <mj-column width="100%">
    <mj-image src="assets/asset_p1_8.png" alt="Protect High-Risk Patients from Shingles with Confidence" href="https://gskpro.com/en-my/products/shingrix/clinical-evidence/efficacy.modernDeeplink.json?modern-deeplink=true&amp;mdmid={{Account.CORE_GSK_MDM_ID__c}}&amp;email={{Account.PersonEmail}}&amp;cc=my_oto_veev_pm-my-sgx-eml-250066_179031&amp;token=7d4c39018d4642e691baf8fcb98ce955&amp;bu=pharma" fluid-on-mobile="true" />
  </mj-column>
</mj-section>

<!-- Salutation & Introduction -->
<mj-section background-color="#ffffff" padding="0px 20px 15px 20px">
  <mj-column width="100%">
    <mj-text font-size="14px" line-height="1.5">
      <strong>Dear {{customText[Prof.|Dr.|Mr.|Ms.]}} {{accFname}} {{accLname}},</strong><br />
      {{customText[Thank you for your time.|Sorry we were not able to meet.|Looking forward to speaking with you.]}}
    </mj-text>
    <mj-text font-size="14px" line-height="1.5" padding-top="12px">
      Here is some information {{customText[I thought you'd find helpful.|that you requested during our conversation.|that complements our conversation.]}}
    </mj-text>
  </mj-column>
</mj-section>

<!-- Patient Case Study Graphic -->
<mj-section background-color="#ffffff" padding="0px 20px 15px 20px">
  <mj-column width="100%">
    <mj-image src="assets/asset_p1_9.png" alt="Meet Mr. J - 67 year old man with Type 2 Diabetes and Heart failure (HF)" fluid-on-mobile="true" />
  </mj-column>
</mj-section>

<!-- Case Study Summary -->
<mj-section background-color="#ffffff" padding="0px 20px 20px 20px">
  <mj-column width="100%">
    <mj-text font-size="14px" line-height="1.5">
      Despite stable management of his chronic conditions, he was hospitalized with urinary symptoms and subsequently developed sudden hearing loss secondary to herpes zoster (HZ). His case underscores the <strong>increased vulnerability of patients with chronic diseases to shingles and its complications.</strong><sup class="sup-tag"><strong>2,3</strong></sup>
    </mj-text>
  </mj-column>
</mj-section>

<!-- Section Heading: Higher Risk -->
<mj-section background-color="#ffffff" padding="0px 20px 12px 20px">
  <mj-column width="100%">
    <mj-text align="center" font-size="20px" font-weight="bold" color="#9e0b0f" line-height="1.3">
      PATIENTS WITH HF AND DIABETES ARE AT HIGHER RISK OF SHINGLES
    </mj-text>
  </mj-column>
</mj-section>

<!-- Risk Stats Infographic -->
<mj-section background-color="#ffffff" padding="0px 20px 20px 20px">
  <mj-column width="100%">
    <mj-image src="assets/asset_p1_10.png" alt="2X higher risk of developing shingles in individuals with HF; 38% increased risk of shingles in adults with diabetes" fluid-on-mobile="true" />
  </mj-column>
</mj-section>

<!-- Section Heading: Vaccinating with Shingrix -->
<mj-section background-color="#ffffff" padding="0px 20px 12px 20px">
  <mj-column width="100%">
    <mj-text align="center" font-size="20px" font-weight="bold" color="#9e0b0f" line-height="1.3">
      PROTECT VULNERABLE PATIENTS WITH DIABETES AND HF FROM SHINGLES; CONSIDER VACCINATING THEM WITH SHINGRIX
    </mj-text>
  </mj-column>
</mj-section>

<!-- Recommendation Banner -->
<mj-section background-color="#ffffff" padding="0px 20px 15px 20px">
  <mj-column width="100%">
    <mj-image src="assets/asset_p1_11.png" alt="National Vaccine-Preventable Disease Recommendations for Older Adults in Malaysia 2024" fluid-on-mobile="true" />
  </mj-column>
</mj-section>

<!-- MSGM Guidebook Title -->
<mj-section background-color="#ffffff" padding="0px 20px 12px 20px">
  <mj-column width="12%" vertical-align="middle">
    <mj-image src="assets/asset_p1_1.png" alt="Guidebook Icon" width="45px" align="left" />
  </mj-column>
  <mj-column width="88%" vertical-align="middle">
    <mj-text font-size="16px" font-weight="bold" color="#9e0b0f" line-height="1.3">
      MSGM National Immunisation Guidebook:<br/>Recommended Immunisation Schedule for Older Adults<sup class="sup-tag">6</sup>
    </mj-text>
  </mj-column>
</mj-section>

<!-- Immunisation Schedule Table Graphic -->
<mj-section background-color="#ffffff" padding="0px 20px 15px 20px">
  <mj-column width="100%">
    <mj-image src="assets/asset_p1_12.png" alt="Recommended Immunisation Schedule Chart" fluid-on-mobile="true" />
  </mj-column>
</mj-section>

<!-- Tax Relief Callout -->
<mj-section background-color="#ffffff" padding="0px 20px 20px 20px">
  <mj-column width="100%">
    <mj-text font-size="14px" line-height="1.5">
      Encourage your patients to stay protected and don't forget to let your patients know they can maximise their tax relief this year!
    </mj-text>
  </mj-column>
</mj-section>

<!-- Red CTA Section -->
<mj-section background-color="#9e0b0f" padding="25px 20px">
  <mj-column width="100%">
    <mj-text align="center" font-size="20px" font-weight="bold" color="#ffffff" line-height="1.3">
      Learn more about protecting your patients with comorbidities on GSKPro
    </mj-text>
    <mj-button background-color="#ffffff" color="#9e0b0f" font-size="16px" font-weight="bold" border-radius="25px" href="https://gskpro.com/en-my/products/shingrix/clinical-evidence/efficacy.modernDeeplink.json?modern-deeplink=true&amp;mdmid={{Account.CORE_GSK_MDM_ID__c}}&amp;email={{Account.PersonEmail}}&amp;cc=my_oto_veev_pm-my-sgx-eml-250066_179032&amp;token=7d4c39018d4642e691baf8fcb98ce955&amp;bu=pharma" padding-top="15px">
      Get full access here
    </mj-button>
  </mj-column>
</mj-section>

<!-- Safety Information -->
<mj-section background-color="#ffffff" padding="20px 20px 15px 20px">
  <mj-column width="100%">
    <mj-text font-size="12px" line-height="1.4">
      <strong>Shingrix Safety Information:</strong><sup class="sup-tag">4</sup><br/>
      <strong>Contraindication:</strong> Hypersensitivity to the active substances or to any component of the vaccine.<br/>
      Very common adverse events include Headache, gastrointestinal symptoms (including nausea, vomiting, diarrhoea and / or abdominal pain), myalgia, injection site reactions (such as pain, redness, swelling), fatigue, chills, fever.
    </mj-text>
    <mj-text font-size="14px" line-height="1.5" padding-top="15px">
      If you have any questions, please contact me if you need more information.<br/>
      Sincerely,
    </mj-text>
  </mj-column>
</mj-section>

<!-- User Contact Card -->
<mj-section background-color="#e6e6e6" padding="15px 20px">
  <mj-column width="10%" vertical-align="top">
    <mj-image src="assets/asset_p1_13.png" alt="Rep Pin" width="30px" align="left" />
  </mj-column>
  <mj-column width="90%" vertical-align="top">
    <mj-text font-size="16px" font-weight="bold" color="#d71920" line-height="1.3">
      {{userName}}
    </mj-text>
    <mj-text font-size="14px" font-weight="bold" color="#151515" padding-top="2px">
      {{User.Title}}
    </mj-text>
    <mj-text font-size="14px" color="#151515" padding-top="4px">
      <strong>Tel</strong> {{User.MobilePhone}} &nbsp;&nbsp; <strong>Email</strong> <a href="mailto:{{User.Email}}" class="link-plain">{{User.Email}}</a>
    </mj-text>
  </mj-column>
</mj-section>

<!-- Feedback Rating Title -->
<mj-section background-color="#ffffff" padding="25px 20px 15px 20px">
  <mj-column width="100%">
    <mj-text align="center" font-size="22px" font-weight="bold" color="#151515">
      How satisfied are you with this email?
    </mj-text>
  </mj-column>
</mj-section>

<!-- Feedback Smilies Rating Grid -->
<mj-section background-color="#ffffff" padding="0px 20px 20px 20px">
  <mj-group>
    <mj-column width="20%">
      <mj-image src="assets/asset_p1_14.png" alt="Very Dissatisfied" width="45px" align="center" href="https://gsk.qualtrics.com/jfe/form/SV_8jBXbvdpv4zkrvo?ENG_2_Embedded=1&amp;ER5=Y&amp;ER6=Y&amp;Cust_1=Y&amp;Foot=N&amp;NOP=1&amp;Brand=SHINGRIX&amp;Channel=1:1Email&amp;Country=Malaysia&amp;ContentLab_Id=PM-MY-SGX-EML-250066&amp;Group=Commercial&amp;Region=EM&amp;Speciality=Dermatology&amp;Therapy_Area=Vaccine&amp;MDM_ID={{Account.CORE_GSK_MDM_ID__c}}&amp;Veeva_ID={{Account.CORE_GSK_Account_Veeva_ID__c}}&amp;EM_NA=Shingrix_Heart_and_Diabetes&amp;Q_Language=EN&amp;token=AAE3272&amp;Qtest=Yes" />
      <mj-text align="center" font-size="12px" font-weight="bold" padding-top="6px">
        <a href="https://gsk.qualtrics.com/jfe/form/SV_8jBXbvdpv4zkrvo?ENG_2_Embedded=1&amp;ER5=Y&amp;ER6=Y&amp;Cust_1=Y&amp;Foot=N&amp;NOP=1&amp;Brand=SHINGRIX&amp;Channel=1:1Email&amp;Country=Malaysia&amp;ContentLab_Id=PM-MY-SGX-EML-250066&amp;Group=Commercial&amp;Region=EM&amp;Speciality=Dermatology&amp;Therapy_Area=Vaccine&amp;MDM_ID={{Account.CORE_GSK_MDM_ID__c}}&amp;Veeva_ID={{Account.CORE_GSK_Account_Veeva_ID__c}}&amp;EM_NA=Shingrix_Heart_and_Diabetes&amp;Q_Language=EN&amp;token=AAE3272&amp;Qtest=Yes" class="link-plain" style="text-decoration:none;color:#151515;">Very dissatisfied</a>
      </mj-text>
    </mj-column>
    <mj-column width="20%">
      <mj-image src="assets/asset_p1_15.png" alt="Dissatisfied" width="45px" align="center" href="https://gsk.qualtrics.com/jfe/form/SV_8jBXbvdpv4zkrvo?ENG_2_Embedded=2&amp;ER5=Y&amp;ER6=Y&amp;Cust_1=Y&amp;Foot=N&amp;NOP=1&amp;Brand=SHINGRIX&amp;Channel=1:1Email&amp;Country=Malaysia&amp;ContentLab_Id=PM-MY-SGX-EML-250066&amp;Group=Commercial&amp;Region=EM&amp;Speciality=Dermatology&amp;Therapy_Area=Vaccine&amp;MDM_ID={{Account.CORE_GSK_MDM_ID__c}}&amp;Veeva_ID={{Account.CORE_GSK_Account_Veeva_ID__c}}&amp;EM_NA=Shingrix_Heart_and_Diabetes&amp;Q_Language=EN&amp;token=AAE3272&amp;Qtest=Yes" />
      <mj-text align="center" font-size="12px" font-weight="bold" padding-top="6px">
        <a href="https://gsk.qualtrics.com/jfe/form/SV_8jBXbvdpv4zkrvo?ENG_2_Embedded=2&amp;ER5=Y&amp;ER6=Y&amp;Cust_1=Y&amp;Foot=N&amp;NOP=1&amp;Brand=SHINGRIX&amp;Channel=1:1Email&amp;Country=Malaysia&amp;ContentLab_Id=PM-MY-SGX-EML-250066&amp;Group=Commercial&amp;Region=EM&amp;Speciality=Dermatology&amp;Therapy_Area=Vaccine&amp;MDM_ID={{Account.CORE_GSK_MDM_ID__c}}&amp;Veeva_ID={{Account.CORE_GSK_Account_Veeva_ID__c}}&amp;EM_NA=Shingrix_Heart_and_Diabetes&amp;Q_Language=EN&amp;token=AAE3272&amp;Qtest=Yes" class="link-plain" style="text-decoration:none;color:#151515;">Dissatisfied</a>
      </mj-text>
    </mj-column>
    <mj-column width="20%">
      <mj-image src="assets/asset_p1_3.png" alt="Neutral" width="45px" align="center" href="https://gsk.qualtrics.com/jfe/form/SV_8jBXbvdpv4zkrvo?ENG_2_Embedded=3&amp;ER5=Y&amp;ER6=Y&amp;Cust_1=Y&amp;Foot=N&amp;NOP=1&amp;Brand=SHINGRIX&amp;Channel=1:1Email&amp;Country=Malaysia&amp;ContentLab_Id=PM-MY-SGX-EML-250066&amp;Group=Commercial&amp;Region=EM&amp;Speciality=Dermatology&amp;Therapy_Area=Vaccine&amp;MDM_ID={{Account.CORE_GSK_MDM_ID__c}}&amp;Veeva_ID={{Account.CORE_GSK_Account_Veeva_ID__c}}&amp;EM_NA=Shingrix_Heart_and_Diabetes&amp;Q_Language=EN&amp;token=AAE3272&amp;Qtest=Yes" />
      <mj-text align="center" font-size="12px" font-weight="bold" padding-top="6px">
        <a href="https://gsk.qualtrics.com/jfe/form/SV_8jBXbvdpv4zkrvo?ENG_2_Embedded=3&amp;ER5=Y&amp;ER6=Y&amp;Cust_1=Y&amp;Foot=N&amp;NOP=1&amp;Brand=SHINGRIX&amp;Channel=1:1Email&amp;Country=Malaysia&amp;ContentLab_Id=PM-MY-SGX-EML-250066&amp;Group=Commercial&amp;Region=EM&amp;Speciality=Dermatology&amp;Therapy_Area=Vaccine&amp;MDM_ID={{Account.CORE_GSK_MDM_ID__c}}&amp;Veeva_ID={{Account.CORE_GSK_Account_Veeva_ID__c}}&amp;EM_NA=Shingrix_Heart_and_Diabetes&amp;Q_Language=EN&amp;token=AAE3272&amp;Qtest=Yes" class="link-plain" style="text-decoration:none;color:#151515;">Neutral</a>
      </mj-text>
    </mj-column>
    <mj-column width="20%">
      <mj-image src="assets/asset_p1_4.png" alt="Satisfied" width="45px" align="center" href="https://gsk.qualtrics.com/jfe/form/SV_8jBXbvdpv4zkrvo?ENG_2_Embedded=4&amp;ER5=Y&amp;ER6=Y&amp;Cust_1=Y&amp;Foot=N&amp;NOP=1&amp;Brand=SHINGRIX&amp;Channel=1:1Email&amp;Country=Malaysia&amp;ContentLab_Id=PM-MY-SGX-EML-250066&amp;Group=Commercial&amp;Region=EM&amp;Speciality=Dermatology&amp;Therapy_Area=Vaccine&amp;MDM_ID={{Account.CORE_GSK_MDM_ID__c}}&amp;Veeva_ID={{Account.CORE_GSK_Account_Veeva_ID__c}}&amp;EM_NA=Shingrix_Heart_and_Diabetes&amp;Q_Language=EN&amp;token=AAE3272&amp;Qtest=Yes" />
      <mj-text align="center" font-size="12px" font-weight="bold" padding-top="6px">
        <a href="https://gsk.qualtrics.com/jfe/form/SV_8jBXbvdpv4zkrvo?ENG_2_Embedded=4&amp;ER5=Y&amp;ER6=Y&amp;Cust_1=Y&amp;Foot=N&amp;NOP=1&amp;Brand=SHINGRIX&amp;Channel=1:1Email&amp;Country=Malaysia&amp;ContentLab_Id=PM-MY-SGX-EML-250066&amp;Group=Commercial&amp;Region=EM&amp;Speciality=Dermatology&amp;Therapy_Area=Vaccine&amp;MDM_ID={{Account.CORE_GSK_MDM_ID__c}}&amp;Veeva_ID={{Account.CORE_GSK_Account_Veeva_ID__c}}&amp;EM_NA=Shingrix_Heart_and_Diabetes&amp;Q_Language=EN&amp;token=AAE3272&amp;Qtest=Yes" class="link-plain" style="text-decoration:none;color:#151515;">Satisfied</a>
      </mj-text>
    </mj-column>
    <mj-column width="20%">
      <mj-image src="assets/asset_p1_5.png" alt="Very Satisfied" width="45px" align="center" href="https://gsk.qualtrics.com/jfe/form/SV_8jBXbvdpv4zkrvo?ENG_2_Embedded=5&amp;ER5=Y&amp;ER6=Y&amp;Cust_1=Y&amp;Foot=N&amp;NOP=1&amp;Brand=SHINGRIX&amp;Channel=1:1Email&amp;Country=Malaysia&amp;ContentLab_Id=PM-MY-SGX-EML-250066&amp;Group=Commercial&amp;Region=EM&amp;Speciality=Dermatology&amp;Therapy_Area=Vaccine&amp;MDM_ID={{Account.CORE_GSK_MDM_ID__c}}&amp;Veeva_ID={{Account.CORE_GSK_Account_Veeva_ID__c}}&amp;EM_NA=Shingrix_Heart_and_Diabetes&amp;Q_Language=EN&amp;token=AAE3272&amp;Qtest=Yes" />
      <mj-text align="center" font-size="12px" font-weight="bold" padding-top="6px">
        <a href="https://gsk.qualtrics.com/jfe/form/SV_8jBXbvdpv4zkrvo?ENG_2_Embedded=5&amp;ER5=Y&amp;ER6=Y&amp;Cust_1=Y&amp;Foot=N&amp;NOP=1&amp;Brand=SHINGRIX&amp;Channel=1:1Email&amp;Country=Malaysia&amp;ContentLab_Id=PM-MY-SGX-EML-250066&amp;Group=Commercial&amp;Region=EM&amp;Speciality=Dermatology&amp;Therapy_Area=Vaccine&amp;MDM_ID={{Account.CORE_GSK_MDM_ID__c}}&amp;Veeva_ID={{Account.CORE_GSK_Account_Veeva_ID__c}}&amp;EM_NA=Shingrix_Heart_and_Diabetes&amp;Q_Language=EN&amp;token=AAE3272&amp;Qtest=Yes" class="link-plain" style="text-decoration:none;color:#151515;">Very satisfied</a>
      </mj-text>
    </mj-column>
  </mj-group>
</mj-section>

<!-- WhatsApp Connect Banner -->
<mj-section background-color="#f0efed" padding="10px 20px">
  <mj-column width="100%">
    <mj-image src="assets/asset_p1_6.png" alt="Stay connected with GSK Malaysia via WhatsApp" href="https://wa.me/60122731841?text=Hi" fluid-on-mobile="true" />
  </mj-column>
</mj-section>

<!-- Footnotes, Abbreviations, References -->
<mj-section background-color="#f0efed" padding="15px 20px 20px 20px">
  <mj-column width="100%">
    <mj-text font-size="11px" color="#151515" line-height="1.4">
      <strong>Footnote:</strong><br/>
      *Systematic review and meta-analysis of 16 studies (four case-control and 12 cohort studies. 868,582 shingles cases; total population with diabetes: 65,541,845) that investigated the risk of shingles among diabetic adults aged &ge;18 years old (diabetes type 1 or 2 only) vs the general population. Study populations varied widely (range: n=750&ndash;51,000,000 adults; median: 272,690 individuals), as did the follow-up periods (range: 1.5&ndash;12 years; median: 5 years).<sup class="sup-tag">5</sup> Absolute risk and incidence rate point estimates not provided in publication.
    </mj-text>
    <mj-text font-size="11px" color="#151515" line-height="1.4" padding-top="10px">
      <strong>Abbreviations:</strong> <strong>HF,</strong> heart failure; <strong>HZ,</strong> herpes zoster; <strong>CI,</strong> Confidence Interval; <strong>ZOE-50,</strong> Zoster Efficacy Study in Adults 50 Years of Age or Older; <strong>ZOE-70,</strong> Zoster Efficacy Study in Adults 70 Years of Age or Older.
    </mj-text>
    <mj-text font-size="11px" color="#151515" line-height="1.4" padding-top="10px">
      <strong>References:</strong><br/>
      <strong>1.</strong> Al-Sardar H. <em>Case Rep Dermatol Med</em>. 2013;2013:738579.<br/>
      <strong>2.</strong> Wu PH, <em>et al</em>, <em>BMC Infect Dis</em>. 2015;15,17.<br/>
      <strong>3.</strong> Munoz-Quiles C, <em>et al</em>. <em>Hum Vaccin Immunother</em>. 2017; 13: 2606-261.<br/>
      <strong>4.</strong> SHINGRIX Prescribing Information.<br/>
      <strong>5.</strong> Huang CT, Lee CY, Sung HY, <em>et al</em>. Association between diabetes mellitus and the risk of herpes zoster: a systematic review and meta-analysis. <em>J Clin Endocrinol Metab.</em> 2022;107:586-597.<br/>
      <strong>6.</strong> Malaysian Society of Geriatric Medicine 2025.
    </mj-text>
    <mj-text font-size="11px" color="#151515" line-height="1.4" padding-top="10px">
      Adverse events should be reported to <a href="mailto:drugsafetyinfo.my@gsk.com" class="link-text">drugsafetyinfo.my@gsk.com</a>.
    </mj-text>
    <mj-text font-size="11px" color="#151515" line-height="1.4" padding-top="6px">
      Trade marks are owned by or licensed to the GSK group of companies.
    </mj-text>
    <mj-text font-size="11px" color="#151515" line-height="1.4" padding-top="6px">
      <strong>Before prescribing, please refer to the full prescribing information.</strong> <a href="https://assets.gskinternet.com/pharma/GSKpro/Malaysia/Shingrix/pi_13188_v_1_0.pdf" class="link-text">Click here</a> to view Shingrix Prescribing Information.
    </mj-text>
  </mj-column>
</mj-section>

<!-- Regulatory & Privacy Footer -->
<mj-section background-color="#e6e6e6" padding="20px 20px">
  <mj-column width="100%">
    <mj-text font-size="11px" line-height="1.4">
      <strong>This email is intended for Malaysia Healthcare Professionals only.</strong>
    </mj-text>
    <mj-text font-size="11px" line-height="1.4" padding-top="8px">
      <strong>About this email:</strong> GSK Malaysia has selected this email to be of interest to you in line with your email preferences, which you can edit or <a href="https://gskpro.com/en-my/communication-preferences/" class="link-text">unsubscribe</a> from at any time. You may also visit the website and update your preferences by logging into the <a href="https://gskpro.com/en-my/communication-preferences/" class="link-text">website</a>.
    </mj-text>
    <mj-text font-size="11px" line-height="1.4" padding-top="8px">
      Please do not reply to this message as this is an inactive mailbox and your email will not be delivered. If you have any comments or questions, please contact us on: GlaxoSmithKline Pharmaceutical Sdn Bhd 195801000141(3277-U) HZ.01, Horizon Penthouse, 1 Powerhouse, 1, Persiaran Bandar Utama, Bandar Utama, 47800 Petaling Jaya, Selangor Darul Ehsan, Malaysia Tel: (603) 2037 9808 <a href="http://my.gsk.com/" class="link-text">www.my.gsk.com</a>.
    </mj-text>
    <mj-text font-size="11px" line-height="1.4" padding-top="8px">
      <strong>About your privacy:</strong> GSK may monitor our technology tools and services (including email, phone, and other communications sent to and from GSK) in order to maintain the security of systems, and to protect our staff, customers and business partners from cyber threats and loss of information. Examples of these monitoring activities include checks for offensive materials, viruses and other malignant code, and unauthorized or unlawful activity. GSK monitoring is conducted with appropriate confidentiality controls and in accordance with local laws. You can learn about the information that we may process about you, and how we use your information, <a href="https://privacy.gsk.com/en-my/pharmaceuticals/default/" class="link-text">here</a>.
    </mj-text>
    <mj-text font-size="11px" line-height="1.4" padding-top="8px">
      You can also view our <a href="https://terms.gsk.com/en-my/pharmaceuticals/default/" class="link-text">terms of use</a>.
    </mj-text>
  </mj-column>
</mj-section>

<!-- Company Details & Registration Info -->
<mj-section background-color="#e6e6e6" padding="0px 20px 20px 20px">
  <mj-column width="15%" vertical-align="middle">
    <mj-image src="assets/asset_p1_7.png" alt="GSK Logo Footer" href="https://gskpro.com/en-my/" width="73px" align="left" />
  </mj-column>
  <mj-column width="85%" vertical-align="middle">
    <mj-text font-size="11px" line-height="1.4">
      &copy; 2025 GSK group of companies or its licensor.
    </mj-text>
  </mj-column>
</mj-section>

<mj-section background-color="#e6e6e6" padding="0px 20px 20px 20px">
  <mj-column width="100%">
    <mj-text font-size="11px" line-height="1.4">
      GlaxoSmithKline Pharmaceutical Sdn Bhd 195801000141(3277-U)<br/>
      HZ.01, Horizon Penthouse, 1 Powerhouse, 1, Persiaran Bandar Utama, Bandar Utama,<br/>
      47800 Petaling Jaya, Selangor Darul Ehsan, Malaysia<br/>
      Tel: (603) 2037 9808
    </mj-text>
  </mj-column>
</mj-section>

<!-- Document Control Code -->
<mj-section background-color="#f0efed" padding="10px 20px 15px 20px">
  <mj-column width="100%">
    <mj-text font-size="11px" color="#151515">
      PM-MY-SGX-EML-250066 12/25
    </mj-text>
  </mj-column>
</mj-section>
"""

# Wrap into full MJML document
full_mjml = f"""<mjml>
  <mj-head>
    <mj-attributes>
      <mj-all font-family="Arial, Helvetica, sans-serif" />
      <mj-text font-size="14px" line-height="1.4" color="#222222" />
    </mj-attributes>
    <mj-style>
      sup {{ font-size: 70% !important; line-height: 0 !important; vertical-align: super !important; }}
      sub {{ font-size: 70% !important; line-height: 0 !important; vertical-align: sub !important; }}
      img {{ -ms-interpolation-mode: bicubic; }}
      a {{ color: inherit; }}
      .link-text {{ color: #d71920 !important; text-decoration: underline; }}
      .link-plain {{ text-decoration: none; color: #151515 !important; }}
    </mj-style>
  </mj-head>
  <mj-body width="700px" background-color="#eef1f4">
    <!-- Header Logo + Text -->
    <mj-section background-color="#ffffff" padding="15px 20px 10px 20px">
      <mj-column width="22%" vertical-align="middle">
        <mj-image src="assets/asset_p1_2.png" alt="GSK Logo" width="125px" align="left" padding="0" href="http://www.gskpro.com/en-my" />
      </mj-column>
      <mj-column width="78%" vertical-align="middle">
        <mj-text font-size="14px" font-weight="bold" color="#151515" line-height="1.3" padding="0 0 0 10px">
          For Registered Malaysia Healthcare Professionals Only
        </mj-text>
      </mj-column>
    </mj-section>

    {raw_mjml_body}
  </mj-body>
</mjml>
"""

pkg_dir = r"c:\Users\SumanBiswas\Downloads\Pages from PM-MY-SGX-EML-250072_ai_package"
output_html_path = os.path.join(pkg_dir, "gemini_compiled_email.html")

res = mrml.to_html(full_mjml)
html_str = res.content if hasattr(res, "content") else str(res)

with open(output_html_path, "w", encoding="utf-8") as f:
    f.write(html_str)

print("SUCCESS: Compiled AI-generated MJML into HTML Email!")
print("Saved to:", output_html_path)
print("HTML Size (bytes):", len(html_str))
