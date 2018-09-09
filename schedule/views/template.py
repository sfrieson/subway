def html (data):
    return """<!DOCTYPE html>
<html>
<head>
  <style>%s</style>
</head>
<body>
  %s
  <script>%s</script>
</body>
</html>
    """ % (data['css'], data['html'], data['js'])
    