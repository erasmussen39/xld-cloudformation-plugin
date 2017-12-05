/**
 * Copyright 2017 XEBIALABS
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */
package com.xebialabs.deployit.plugin.aws.support;

import de.schlichtherle.truezip.file.TFile;

import java.io.ByteArrayOutputStream;
import java.net.URI;
import java.net.URL;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

public class BotoLoader {


    public static List<String> listAvailableServices() throws Exception {
        List<String> availableServices = new ArrayList<>();
        List<TFile> tFiles = serviceDir();
        for (TFile tFile : tFiles) {
            availableServices.add(tFile.getName());
        }
        Collections.sort(availableServices);
        return availableServices;
    }

    private static List<TFile> serviceDir() throws Exception {
        List<TFile> tFiles = new ArrayList<>();
        URL url = BotoLoader.class.getClassLoader().getResource("botocore/data");
        TFile tFile = new TFile(url.toURI());
        TFile[] listFiles = tFile.listFiles();
        tFiles.addAll(Arrays.asList(listFiles));
        return tFiles;
    }

    public static List<String> listApiVersion(String serviceName, String typeName) throws Exception {
        List<TFile> tFiles = serviceDir();
        List<String> apiVersions = new ArrayList<>();
        for (TFile tFile : tFiles) {
            if (tFile.getName().equals(serviceName)) {
                apiVersions.addAll(Arrays.asList(tFile.list()));
            }
        }
        return apiVersions;
    }

    public static String fullpath(String name) throws Exception {
        URL url = BotoLoader.class.getClassLoader().getResource("boto3/data");
        TFile tFile = new TFile(url.toURI());
        return tFile.getPath() + name;
    }

    public static String loadFile(String name) throws Exception {
        String unixName = name.replace("\\", "/");
        unixName = unixName + ".json";
        URL url = getBotoResourceUrl(unixName, BotoLoader.class.getClassLoader());
        if (url == null) {
            url = getBotoResourceUrl(unixName, Thread.currentThread().getContextClassLoader());
        }
        if (url == null) {
            url = getBotoResourceUrl(unixName, ClassLoader.getSystemClassLoader());
        }
        if (url == null) {
            throw new RuntimeException("Cannot load file '"+ unixName + "' from classpath locations 'boto3/data/' or 'botocore/data/'");
        }
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        URI uri = url.toURI();
        new TFile(uri).output(out);
        String content = out.toString();
        return content;
    }

    private static URL getBotoResourceUrl(String unixName, ClassLoader classLoader) {
        String resourceName = "boto3/data/" + unixName;
        URL url = classLoader.getResource(resourceName);
        if (url == null) {
            url = classLoader.getResource("botocore/data/" + unixName);
        }
        return url;
    }

    private static ClassLoader getClassLoaderOfClass(final Class<?> clazz) {
        ClassLoader cl = clazz.getClassLoader();
        if (cl == null) {
            return ClassLoader.getSystemClassLoader();
        } else {
            return cl;
        }
    }

    private static URL getResource(String resource, ClassLoader classLoader) {
        return classLoader.getResource(resource);
    }

    public static URL getResourceBySelfClassLoader(String resource) {
        return getResource(resource, getClassLoaderOfClass(BotoLoader.class));
    }

}
