import mrml

mjml_code = """
<mjml>
  <mj-head>
    <mj-attributes>
      <mj-all font-family="Arial, sans-serif" />
    </mj-attributes>
  </mj-head>
  <mj-body width="700px" background-color="#eef1f4">
    <mj-section background-color="#ffffff" padding="20px">
      <mj-column>
        <mj-text font-size="22px" font-weight="bold" color="#9e0b0f">
          Hello MJML World!
        </mj-text>
        <mj-text font-size="14px" color="#333333">
          This is a 100% bulletproof email template powered by MRML/MJML.
        </mj-text>
        <mj-button background-color="#9e0b0f" color="#ffffff" border-radius="20px" href="https://gskpro.com">
          Get Full Access &raquo;
        </mj-button>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>
"""

output = mrml.to_html(mjml_code)
html_str = str(output) if hasattr(output, 'content') == False else output.content
print("Output type:", type(output), "dir:", dir(output))
if hasattr(output, 'content'):
    html_str = output.content
else:
    html_str = str(output)
print("SUCCESS: Length of HTML:", len(html_str))
