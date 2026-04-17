streamlit.errors.StreamlitDuplicateElementId: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).

Traceback:
File "/mount/src/b2b-parts-portal/app.py", line 35, in <module>
    customer_dashboard()
    ~~~~~~~~~~~~~~~~~~^^
File "/mount/src/b2b-parts-portal/customer.py", line 150, in customer_dashboard
    if st.button("Add"):
       ~~~~~~~~~^^^^^^^
File "/home/adminuser/venv/lib/python3.14/site-packages/streamlit/runtime/metrics_util.py", line 563, in wrapped_func
    result = non_optional_func(*args, **kwargs)
File "/home/adminuser/venv/lib/python3.14/site-packages/streamlit/elements/widgets/button.py", line 379, in button
    return self.dg._button(
           ~~~~~~~~~~~~~~~^
        label,
        ^^^^^^
    ...<12 lines>...
        shortcut=shortcut,
        ^^^^^^^^^^^^^^^^^^
    )
    ^
File "/home/adminuser/venv/lib/python3.14/site-packages/streamlit/elements/widgets/button.py", line 1648, in _button
    element_id = compute_and_register_element_id(
        "form_submit_button" if is_form_submitter else "button",
    ...<10 lines>...
        shortcut=normalized_shortcut,
    )
File "/home/adminuser/venv/lib/python3.14/site-packages/streamlit/elements/lib/utils.py", line 265, in compute_and_register_element_id
    _register_element_id(ctx, element_type, element_id)
    ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.14/site-packages/streamlit/elements/lib/utils.py", line 150, in _register_element_id
    raise StreamlitDuplicateElementId(element_type)
