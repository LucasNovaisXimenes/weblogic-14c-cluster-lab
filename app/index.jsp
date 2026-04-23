<%@ page import="java.net.InetAddress, java.sql.*, javax.naming.*, javax.sql.DataSource" %>
<html>
<head><title>Hello WebLogic + DS</title></head>
<body>
<h1>Hello do WebLogic!</h1>
<p><b>Servidor:</b> <%= System.getProperty("weblogic.Name") %></p>
<p><b>Host:</b> <%= InetAddress.getLocalHost().getHostName() %></p>
<p><b>Data:</b> <%= new java.util.Date() %></p>

<hr/>
<h2>Consulta no banco (via Data Source jdbc/LabDS)</h2>

<%
    Connection conn = null;
    Statement  stmt = null;
    ResultSet  rs   = null;
    try {
        InitialContext ctx = new InitialContext();
        DataSource ds = (DataSource) ctx.lookup("jdbc/LabDS");
        conn = ds.getConnection();
        stmt = conn.createStatement();
        rs = stmt.executeQuery("SELECT id, nome, cargo FROM funcionarios ORDER BY id");
%>
        <table border="1" cellpadding="6" cellspacing="0">
            <tr><th>ID</th><th>Nome</th><th>Cargo</th></tr>
<%
        while (rs.next()) {
%>
            <tr>
              <td><%= rs.getInt("id") %></td>
              <td><%= rs.getString("nome") %></td>
              <td><%= rs.getString("cargo") %></td>
            </tr>
<%
        }
%>
        </table>
<%
    } catch (Exception e) {
%>
        <p style="color:red"><b>Erro:</b> <%= e.getMessage() %></p>
        <pre><% e.printStackTrace(new java.io.PrintWriter(out)); %></pre>
<%
    } finally {
        if (rs   != null) try { rs.close();   } catch (Exception ignore) {}
        if (stmt != null) try { stmt.close(); } catch (Exception ignore) {}
        if (conn != null) try { conn.close(); } catch (Exception ignore) {}
    }
%>

</body>
</html>
