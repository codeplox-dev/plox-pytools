API Reference
=============

This page contains auto-generated API reference documentation.

.. toctree::
   :titlesonly:

   {% for page in pages | sort %}
   {#
      bc we use namespace package without a toplevel __init__.py
   #}
   {% if (page.top_level_object or page.name.split('.') | length == 2) and page.display %}
   plox.{{ page.short_name }} <{{ page.include_path }}>
   {% endif %}
   {% endfor %}
